"""Retry 3 failed augmented tasks: Anti, Vouchers, Bus Stops
Single mode, 1200s timeout per call."""

import json, sys, subprocess, os, tempfile, time, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import httpx

LOGIC_API_URL = "https://ejentum-main-ab125c3.zuplo.app/logicv1/"
WEBHOOK_SECRET = "4bc2c650b7509f2b54de785e8d753df4a5b50d8eed47bbc76b59e67b3a14a581"
MODEL = "opus"
TIMEOUT = 1200

def call_logic_api(query, mode="reasoning"):
    try:
        resp = httpx.post(LOGIC_API_URL, headers={"X-Zuplo-Secret": WEBHOOK_SECRET, "Content-Type": "application/json"},
                          json={"query": query, "mode": mode}, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list) and len(data) > 0:
            return data[0].get(f"{mode}_ability", "")
        return None
    except Exception as e:
        print(f"  [API ERR: {e}]", flush=True)
        return None

def call_claude(prompt, system=""):
    full = system + "\n\n" + prompt if system else prompt
    f_path = os.path.join(tempfile.gettempdir(), "_lcb_retry.txt")
    with open(f_path, "w", encoding="utf-8") as f:
        f.write(full)
    cmd = f'type "{f_path}" | claude -p --model {MODEL} --effort max --no-session-persistence'
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT,
                              shell=True, encoding="utf-8", errors="replace", cwd=tempfile.gettempdir())
    except subprocess.TimeoutExpired:
        print(f"  [TIMEOUT at {TIMEOUT}s]", flush=True)
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() if proc.stdout else None

def extract_code(response):
    if not response: return ""
    if "```python" in response:
        return response.split("```python")[1].split("```")[0].strip()
    elif "```" in response:
        code = response.split("```")[1].split("```")[0].strip()
        if code.split("\n")[0].strip() in ("python","py"):
            code = "\n".join(code.split("\n")[1:])
        return code
    return response

def build_prompt(task):
    pub = json.loads(task["public_test_cases"]) if isinstance(task["public_test_cases"], str) else task["public_test_cases"]
    parts = [f"## Problem: {task['question_title']}\n", task["question_content"]]
    if pub:
        parts.append("\n## Examples:")
        for t in pub[:3]:
            parts.append(f"\nInput:\n```\n{t['input'].strip()}\n```\nOutput:\n```\n{t['output'].strip()}\n```")
    parts.append("\nWrite a complete Python solution reading from stdin, writing to stdout.")
    return "\n".join(parts)

def evaluate(code, task):
    pub = json.loads(task["public_test_cases"]) if isinstance(task["public_test_cases"], str) else task["public_test_cases"]
    if not pub or not code.strip():
        return {"pass": False, "tests_run": 0, "tests_passed": 0}
    results = []
    for i, test in enumerate(pub):
        f_path = os.path.join(tempfile.gettempdir(), f"_lcb_r_{i}.py")
        with open(f_path, "w", encoding="utf-8") as f:
            f.write(code)
        try:
            p = subprocess.run([sys.executable, f_path], input=test["input"], capture_output=True,
                               text=True, timeout=30, encoding="utf-8", errors="replace")
            results.append(p.stdout.strip() == test["output"].strip())
        except:
            results.append(False)
    return {"pass": all(results), "tests_run": len(results), "tests_passed": sum(results)}

SYSTEM = ("You are an expert competitive programmer. Solve the problem below.\n"
          "Write a complete Python solution that reads from stdin and writes to stdout.\n"
          "Return ONLY the code inside a ```python code block. No explanations.")

DECISION_SYSTEM = ("You are an expert competitive programmer. Your job is NOT to write code. "
                   "Describe your reasoning challenge for this problem in 1-2 sentences. "
                   "Respond with ONLY:\nquery: <your reasoning challenge>")

INJECTION_PREAMBLE = ("Before writing code, absorb this reasoning injection:\n\n"
                     "[REASONING INJECTION]\n{injection}\n[END INJECTION]\n\n"
                     "Apply it:\n- [NEGATIVE GATE]: the algorithmic trap to avoid\n"
                     "- [REASONING TOPOLOGY]: follow as your decision structure\n"
                     "- Suppress: signals -- scan your approach against these\n"
                     "- [FALSIFICATION TEST]: verify before finalizing\n\n"
                     "Now write the solution.\n\n")

# Load tasks
tasks_to_retry = []
with open("c:/Users/frank/Desktop/ejentum/benchmarks-staging/lcb-hard/lcb_tasks_batch1.json") as f:
    b1 = json.load(f)
for t in b1:
    if t["question_title"] in ("Anti", "Vouchers"):
        tasks_to_retry.append(t)

with open("c:/Users/frank/Desktop/ejentum/benchmarks-staging/lcb-hard/lcb_tasks_batch3.json") as f:
    b3 = json.load(f)
for t in b3:
    if t["question_title"] == "Bus Stops":
        tasks_to_retry.append(t)

print(f"=== RETRY: {len(tasks_to_retry)} tasks | single mode | {TIMEOUT}s timeout ===", flush=True)
for t in tasks_to_retry:
    print(f"  {t['question_title']}", flush=True)

results = []
for task in tasks_to_retry:
    title = task["question_title"]
    print(f"\n{'='*60}", flush=True)
    print(f"RETRYING: {title}", flush=True)
    print(f"{'='*60}", flush=True)

    task_prompt = build_prompt(task)
    start = time.time()

    # Decision pass
    print("  Pass 1: Decision...", flush=True)
    dec_resp = call_claude(task_prompt, DECISION_SYSTEM)
    query = f"Solve hard competitive programming: {title}"
    if dec_resp:
        qm = re.search(r"query:\s*(.+)", dec_resp, re.IGNORECASE)
        if qm:
            query = qm.group(1).strip()
    print(f"  Query: {query[:80]}", flush=True)

    # API call
    print("  Pass 2: Injection...", flush=True)
    injection = call_logic_api(query, "reasoning")
    injection_len = len(injection) if injection else 0
    print(f"  Injection: {injection_len} chars", flush=True)

    # Code pass
    print("  Pass 3: Code generation...", flush=True)
    if injection:
        augmented_prompt = INJECTION_PREAMBLE.format(injection=injection) + task_prompt
    else:
        augmented_prompt = task_prompt
    response = call_claude(augmented_prompt, SYSTEM)

    elapsed = time.time() - start
    code = extract_code(response)
    eval_result = evaluate(code, task)

    status = "PASS" if eval_result["pass"] else f"FAIL ({eval_result['tests_passed']}/{eval_result['tests_run']})"
    print(f"\n  RESULT: {status} | {len(code)} chars | {elapsed:.0f}s", flush=True)

    results.append({
        "title": title,
        "code_length": len(code),
        "elapsed": elapsed,
        "eval": eval_result,
        "injection_length": injection_len,
        "query": query[:200],
        "code": code,
    })

print(f"\n{'='*60}", flush=True)
print(f"RETRY SUMMARY", flush=True)
print(f"{'='*60}", flush=True)
for r in results:
    status = "PASS" if r["eval"]["pass"] else "FAIL"
    print(f"  {r['title']:28} | {status} | {r['code_length']}ch | {r['elapsed']:.0f}s", flush=True)

passed = sum(1 for r in results if r["eval"]["pass"])
print(f"\nRetry: {passed}/{len(results)} passed", flush=True)

out = "c:/Users/frank/Desktop/ejentum/benchmarks-staging/lcb-hard/results/retry_results.json"
with open(out, "w") as f:
    json.dump(results, f, indent=2, default=str)
print(f"Saved: {out}", flush=True)
