"""
LiveCodeBench Hard Runner v3 — Task-Specific Cognitive Routing
===============================================================
Redesigned decision pass forces deep cognitive pre-analysis before
querying the Logic API. Produces targeted queries that route to
diverse abilities instead of the same generic injection.

Key differences from v2:
  - Cognitive pre-analysis pass (4 risk categories)
  - Query must describe REASONING FAILURE MODE, not topic
  - Examples of good vs bad queries in prompt
  - Multi mode option for compound cognitive demands
  - Full skill file integration

Usage:
    python run_lcb_v3.py --condition augmented
    python run_lcb_v3.py --condition both
    python run_lcb_v3.py --condition augmented --mode multi
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import httpx

# ---------- Configuration ----------

LOGIC_API_URL = "https://ejentum-main-ab125c3.zuplo.app/logicv1/"
API_KEY = os.environ.get("EJENTUM_API_KEY", "")

N8N_URL = "https://ejentum-main-ab125c3.zuplo.app/logicv1/"
WEBHOOK_SECRET = "4bc2c650b7509f2b54de785e8d753df4a5b50d8eed47bbc76b59e67b3a14a581"

RESULTS_DIR = Path(__file__).parent / "results"
MODEL = "opus"
SKILL_FILE = Path(__file__).parent.parent.parent / "DOCS" / "external" / "skill.md"

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ---------- Logic API ----------

def call_logic_api(query, mode="reasoning"):
    """Call n8n direct webhook with webhook secret. Bypasses Zuplo."""
    try:
        resp = httpx.post(
            N8N_URL,
            headers={"Content-Type": "application/json", "X-Zuplo-Secret": WEBHOOK_SECRET},
            json={"query": query, "mode": mode},
            timeout=15.0,
        )
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list) and len(data) > 0:
            ability = data[0].get(f"{mode}_ability", "")
            if ability:
                return ability
    except Exception as e:
        print(f" [API ERR: {e}]", end="", flush=True)
    return None


# ---------- Claude CLI ----------

def call_claude(prompt, timeout=1200, effort="max"):
    input_file = os.path.join(tempfile.gettempdir(), "_lcb_v3_input.txt")
    with open(input_file, "w", encoding="utf-8") as f:
        f.write(prompt)
    cmd = f'type "{input_file}" | claude -p --model {MODEL} --effort {effort} --no-session-persistence'
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                              shell=True, encoding="utf-8", errors="replace",
                              cwd=tempfile.gettempdir())
    except subprocess.TimeoutExpired:
        print(" [TIMEOUT]", end="", flush=True)
        return None
    if proc.returncode != 0:
        print(f" [EXIT {proc.returncode}]", end="", flush=True)
        return None
    return proc.stdout.strip() if proc.stdout else None


# ---------- Code extraction ----------

def extract_code(response):
    if not response:
        return ""
    if "```python" in response:
        blocks = re.findall(r"```python\s*\n(.*?)```", response, re.DOTALL)
        return blocks[-1].strip() if blocks else ""
    if "```" in response:
        blocks = re.findall(r"```\s*\n(.*?)```", response, re.DOTALL)
        return blocks[-1].strip() if blocks else ""
    return response.strip()


# ---------- Evaluation ----------

def evaluate_solution(code, test_cases):
    if not code.strip():
        return {"pass": False, "tests_run": 0, "tests_passed": 0}
    tests = json.loads(test_cases) if isinstance(test_cases, str) else test_cases
    passed = 0
    for tc in tests:
        inp = tc.get("input", "")
        expected = tc.get("output", "").strip()
        try:
            proc = subprocess.run(
                ["python", "-c", code],
                input=inp, capture_output=True, text=True, timeout=30,
                encoding="utf-8", errors="replace",
            )
            actual = proc.stdout.strip()
            if actual == expected:
                passed += 1
        except Exception:
            pass
    return {"pass": passed == len(tests), "tests_run": len(tests), "tests_passed": passed}


# ---------- Prompts ----------

TOOL_CALL_PROMPT = """{skill_file}

---

You have access to the Ejentum Logic API. Call it before solving this task.

**Task:** {title}
{task_brief}

Describe the task structure and identify which reasoning domain fits best (Causal, Temporal, Spatial, Simulation, Abstraction, or Metacognition). Output your API call:

```json
{{"query": "reasoning domain + task description", "mode": "single or multi"}}
```"""


CODE_WITH_SCAFFOLD_PROMPT = """You called the Ejentum Logic API and received this reasoning injection:

[REASONING CONTEXT]
{injection}
[END REASONING CONTEXT]

Follow the skill file: ABSORB the injection. Read the NEGATIVE GATE. Follow the REASONING TOPOLOGY. Apply Suppress signals as post-check.

Now solve this competitive programming problem. Read from stdin, write to stdout.

{task_description}

Write ONLY the Python solution code. No explanation."""


def extract_task_summary(title, description):
    """Extract constraints and one-line summary from task description."""
    constraints = []
    for line in description.split("\n"):
        line = line.strip()
        if any(c in line for c in ["\\le", "<=", "\\leq"]) and any(c in line for c in ["10^", "10**", "000"]):
            constraints.append(line)
        elif re.match(r'^[-\s]*\d+\s*[<]\s*\w+\s*[<]\s*\d', line):
            constraints.append(line)
    constraint_str = "; ".join(constraints[:4]) if constraints else "Hard difficulty, competitive programming"
    if len(constraint_str) > 300:
        constraint_str = constraint_str[:300]

    summary = title
    for para in description.split("\n\n"):
        para = para.strip()
        if para and not para.startswith("Input") and not para.startswith("Output") and not para.startswith("Sample") and not para.startswith("```") and len(para) > 20:
            first_sentence = para.split(".")[0].strip()
            if len(first_sentence) > 15:
                summary = first_sentence[:200]
                break

    return constraint_str, summary


BASELINE_PROMPT = """Solve this competitive programming problem. Read from stdin, write to stdout.

{task_description}

Write ONLY the Python solution code. No explanation."""


# ---------- Parse query from analysis ----------

def extract_api_call(response):
    """Extract the JSON API call from the model's tool-call output."""
    if not response:
        return None, "reasoning"

    query = None
    mode = "reasoning"

    # Try to find JSON block in ```json ... ``` or raw JSON
    json_match = re.search(r'```json\s*\n?\s*(\{.*?\})\s*\n?\s*```', response, re.DOTALL)
    if not json_match:
        json_match = re.search(r'(\{"query":\s*".*?".*?\})', response, re.DOTALL)
    if not json_match:
        # Try to find bare JSON object
        json_match = re.search(r'\{[^}]*"query"[^}]*\}', response, re.DOTALL)

    if json_match:
        try:
            obj = json.loads(json_match.group(1) if json_match.lastindex else json_match.group(0))
            query = obj.get("query", "")
            mode = obj.get("mode", "reasoning")
            if mode not in ("reasoning", "reasoning-multi"):
                mode = "reasoning"
        except json.JSONDecodeError:
            pass

    # Fallback: try QUERY:/MODE: markers
    if not query:
        q_match = re.search(r'(?:QUERY|query)\s*[:=]\s*["\']?(.+?)(?:["\']?\s*$|["\']?\s*\n)', response, re.MULTILINE)
        if q_match:
            query = q_match.group(1).strip().strip('"\'')

    if not query:
        m_match = re.search(r'(?:MODE|mode)\s*[:=]\s*["\']?(.+?)(?:["\']?\s*$|["\']?\s*\n)', response, re.MULTILINE)
        if m_match:
            m = m_match.group(1).strip().strip('"\'').lower()
            if "multi" in m:
                mode = "reasoning-multi"

    # Last resort fallback
    if not query:
        lines = [l.strip() for l in response.strip().split("\n") if l.strip() and len(l.strip()) > 30]
        if lines:
            query = lines[-1][:200]

    return query, mode


# ---------- Main ----------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--condition", choices=["baseline", "augmented", "both"], default="augmented")
    parser.add_argument("--mode", choices=["reasoning", "reasoning-multi", "auto"], default="auto",
                        help="API mode: single, multi, or auto (model decides via skill file)")
    parser.add_argument("--run-id", default="v3")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--tasks", type=str, default=None, help="Comma-separated task titles to run")
    args = parser.parse_args()

    # Load tasks from all batch files
    base_dir = Path(__file__).parent
    task_map = {}
    for batch in ["lcb_tasks_batch1.json", "lcb_tasks_batch2.json", "lcb_tasks_batch3.json"]:
        fpath = base_dir / batch
        if fpath.exists():
            with open(fpath, encoding="utf-8") as f:
                for t in json.load(f):
                    task_map[t["question_title"]] = t
    all_tasks = [t for t in task_map.values() if t.get("difficulty") == "hard"]
    all_tasks.sort(key=lambda t: t["question_title"])

    # Exclude known unsolvable tasks
    exclude = {"Anti", "Vouchers", "Bus Stops", "Prerequisites", "Shortcuts"}
    all_tasks = [t for t in all_tasks if t["question_title"] not in exclude]

    if args.tasks:
        selected = set(args.tasks.split(","))
        all_tasks = [t for t in all_tasks if t["question_title"] in selected]

    # Load skill file
    skill_text = ""
    if SKILL_FILE.exists():
        with open(SKILL_FILE, encoding="utf-8") as f:
            skill_text = f.read()
        print(f"Skill file loaded: {len(skill_text)} chars")
    else:
        print(f"WARNING: Skill file not found at {SKILL_FILE}")

    run_dir = RESULTS_DIR / f"{args.condition}_{args.run_id}"
    run_dir.mkdir(parents=True, exist_ok=True)
    log_file = RESULTS_DIR / f"lcb_{args.run_id}_log.txt"

    conditions = ["baseline", "augmented"] if args.condition == "both" else [args.condition]

    for condition in conditions:
        print(f"\n{'='*60}")
        print(f"CONDITION: {condition.upper()} | MODE: {args.mode} | RUN: {args.run_id}")
        print(f"{'='*60}")

        results = []
        for i, task in enumerate(all_tasks):
            task_num = i + 1
            if task_num < args.start:
                continue

            title = task["question_title"]
            desc = task["question_content"]
            tests = task.get("public_test_cases", "[]")

            print(f"\n[{task_num}/{len(all_tasks)}] {title}")

            t0 = time.time()

            if condition == "baseline":
                # Baseline: single call, no augmentation
                prompt = BASELINE_PROMPT.format(task_description=desc)
                print(f"  Baseline call...", end="", flush=True)
                response = call_claude(prompt)
                elapsed = time.time() - t0
                code = extract_code(response)
                if code:
                    print(f" {elapsed:.0f}s, {len(code)}ch")
                else:
                    print(f" FAILED ({elapsed:.0f}s)")

                ev = evaluate_solution(code, tests)
                result = {
                    "title": title, "difficulty": "hard", "platform": "atcoder",
                    "condition": "baseline",
                    "code": code, "code_length": len(code),
                    "elapsed_seconds": round(elapsed, 1),
                    "eval": ev,
                }

            else:
                # Augmented v3: cognitive pre-analysis → API → code

                # STEP 1: Model makes tool call (reads skill file + task brief, outputs API request)
                task_brief = desc[:300].rsplit(" ", 1)[0] + "..."
                print(f"  Tool call...", end="", flush=True)
                tool_prompt = TOOL_CALL_PROMPT.format(
                    skill_file=skill_text, title=title, task_brief=task_brief
                )
                t1 = time.time()
                tool_response = call_claude(tool_prompt, timeout=180)
                t1_elapsed = time.time() - t1

                query, chosen_mode = extract_api_call(tool_response) if tool_response else (None, "reasoning")
                if query:
                    print(f" {t1_elapsed:.0f}s, query={len(query)}ch, mode={chosen_mode}")
                    print(f"  Query: {query[:150]}")
                else:
                    print(f" FAILED ({t1_elapsed:.0f}s), using title as fallback")
                    query = f"Solve competitive programming task: {title}"
                    chosen_mode = "reasoning"

                # Override mode if CLI flag forces it
                api_mode = args.mode if args.mode != "auto" else chosen_mode

                # STEP 2: Execute the tool call (Logic API via n8n direct)
                print(f"  Logic API ({api_mode})...", end="", flush=True)
                injection = call_logic_api(query, mode=api_mode)
                if injection:
                    print(f" {len(injection)}ch")
                else:
                    print(f" FAILED (proceeding without)")
                    injection = ""

                # STEP 3: Return result + solve (model receives injection and writes code)
                print(f"  Code gen...", end="", flush=True)
                code_prompt = CODE_WITH_SCAFFOLD_PROMPT.format(
                    injection=injection, task_description=desc
                )
                t3 = time.time()
                response = call_claude(code_prompt)
                t3_elapsed = time.time() - t3
                elapsed = time.time() - t0
                code = extract_code(response)

                if code:
                    print(f" {t3_elapsed:.0f}s, {len(code)}ch (total: {elapsed:.0f}s)")
                else:
                    print(f" FAILED ({t3_elapsed:.0f}s)")

                ev = evaluate_solution(code, tests)
                result = {
                    "title": title, "difficulty": "hard", "platform": "atcoder",
                    "condition": "augmented_v3",
                    "code": code, "code_length": len(code),
                    "elapsed_seconds": round(elapsed, 1),
                    "eval": ev,
                    "api_called": True,
                    "api_mode": api_mode,
                    "model_chose_mode": chosen_mode,
                    "api_query": query,
                    "injection_length": len(injection) if injection else 0,
                    "injection_received": bool(injection),
                    "tool_call_text": tool_response or "",
                    "tool_call_length": len(tool_response) if tool_response else 0,
                    "tool_call_time": round(t1_elapsed, 1),
                    "code_time": round(t3_elapsed, 1),
                }

            # Evaluate
            status = "PASS" if ev["pass"] else "FAIL"
            print(f"  Result: {status} ({ev['tests_passed']}/{ev['tests_run']})")

            results.append(result)

            # Save incremental
            out_path = run_dir / f"{task_num:02d}_{title.replace(' ', '_').lower()}.json"
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

        # Save combined
        combined_path = run_dir / "results_full.json"
        with open(combined_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        # Summary
        passed = sum(1 for r in results if r["eval"]["pass"])
        total = len(results)
        print(f"\n{'='*60}")
        print(f"{condition.upper()} COMPLETE: {passed}/{total} ({passed/total*100:.1f}%)")
        if condition != "baseline":
            queries = [r.get("api_query", "") for r in results if r.get("api_query")]
            injections = [r.get("injection_length", 0) for r in results]
            unique_injections = len(set(s for s in injections if s > 0))
            print(f"Injection diversity: {unique_injections} unique sizes out of {len(injections)}")
            print(f"Query lengths: min={min(len(q) for q in queries)}, avg={sum(len(q) for q in queries)//len(queries)}, max={max(len(q) for q in queries)}")
        print(f"{'='*60}")


if __name__ == "__main__":
    main()
