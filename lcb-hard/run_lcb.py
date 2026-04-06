"""
LiveCodeBench Hard Runner — Skill File v2 (Decision Pass)
===========================================================
A/B test on competitive programming problems (stdin/stdout).

Baseline: Standard prompt, model writes solution.
Augmented: Skill file + decision pass. Model decides CALL or SKIP per task.

Usage:
    python run_lcb.py --condition baseline
    python run_lcb.py --condition augmented
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

LOGIC_API_URL = os.environ.get("EJENTUM_API_URL", "https://ejentum-main-ab125c3.zuplo.app/logicv1/")
API_KEY = os.environ.get("EJENTUM_API_KEY", "")

RESULTS_DIR = Path(__file__).parent / "results"
MODEL = "opus"
TASKS_FILE = Path(__file__).parent / "lcb_tasks.json"
SKILL_FILE = Path(__file__).parent / "skill.md"  # Place your Ejentum skill file here

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ---------- Logic API ----------

def call_logic_api(query, mode="single"):
    try:
        resp = httpx.post(
            LOGIC_API_URL,
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json={"query": query, "mode": mode},
            timeout=10.0,
        )
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list) and len(data) > 0:
            return data[0].get(f"{mode}_ability", "")
        return None
    except Exception as e:
        print(f" [API ERR: {e}]", end="", flush=True)
        return None


# ---------- Claude CLI ----------

def call_claude(prompt, system_prompt=""):
    full_input = system_prompt + "\n\n" + prompt if system_prompt else prompt
    input_file = os.path.join(tempfile.gettempdir(), "_lcb_input.txt")
    with open(input_file, "w", encoding="utf-8") as f:
        f.write(full_input)

    cmd = f'type "{input_file}" | claude -p --model {MODEL} --effort max --no-session-persistence'
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600,
                              shell=True, encoding="utf-8", errors="replace",
                              cwd=tempfile.gettempdir())
    except subprocess.TimeoutExpired:
        print(" [TIMEOUT]", end="", flush=True)
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() if proc.stdout else None


# ---------- Code extraction ----------

def extract_code(response):
    if not response:
        return ""
    if "```python" in response:
        blocks = response.split("```python")
        if len(blocks) > 1:
            return blocks[1].split("```")[0].strip()
    elif "```" in response:
        blocks = response.split("```")
        if len(blocks) > 1:
            code = blocks[1].split("```")[0].strip()
            first_line = code.split("\n")[0].strip()
            if first_line in ("python", "py", "Python"):
                code = "\n".join(code.split("\n")[1:])
            return code
    # Fallback
    lines = response.strip().split("\n")
    code_lines = []
    in_code = False
    for line in lines:
        if line.startswith("import ") or line.startswith("from ") or line.startswith("def ") or line.startswith("import sys") or "input()" in line or in_code:
            in_code = True
            code_lines.append(line)
    return "\n".join(code_lines) if code_lines else response


# ---------- Evaluation ----------

def evaluate_solution(code, task):
    """Run solution against public test cases. Returns pass/fail per test."""
    pub_tests = json.loads(task['public_test_cases']) if isinstance(task['public_test_cases'], str) else task['public_test_cases']
    if not pub_tests or not code.strip():
        return {"pass": False, "tests_run": 0, "tests_passed": 0, "reason": "empty"}

    results = []
    for i, test in enumerate(pub_tests):
        test_input = test['input']
        expected = test['output'].strip()

        # Write code to temp file
        code_file = os.path.join(tempfile.gettempdir(), f"_lcb_sol_{i}.py")
        with open(code_file, "w", encoding="utf-8") as f:
            f.write(code)

        try:
            proc = subprocess.run(
                [sys.executable, code_file],
                input=test_input, capture_output=True, text=True,
                timeout=30, encoding="utf-8", errors="replace",
            )
            actual = proc.stdout.strip()
            passed = actual == expected
            results.append({"passed": passed, "expected": expected[:100], "actual": actual[:100]})
        except subprocess.TimeoutExpired:
            results.append({"passed": False, "expected": expected[:100], "actual": "TIMEOUT"})
        except Exception as e:
            results.append({"passed": False, "expected": expected[:100], "actual": str(e)[:100]})

    all_pass = all(r['passed'] for r in results)
    n_pass = sum(1 for r in results if r['passed'])
    return {"pass": all_pass, "tests_run": len(results), "tests_passed": n_pass, "details": results}


# ---------- Prompts ----------

BASELINE_SYSTEM = (
    "You are an expert competitive programmer. Solve the problem below.\n"
    "Write a complete Python solution that reads from stdin and writes to stdout.\n"
    "Return ONLY the code inside a ```python code block. No explanations."
)

CODE_SYSTEM = BASELINE_SYSTEM


def load_skill_file():
    if SKILL_FILE.exists():
        return SKILL_FILE.read_text(encoding="utf-8")
    return ""


def build_decision_system(skill_content):
    return (
        "You are an expert competitive programmer with access to a reasoning "
        "augmentation tool. Your job right now is NOT to write code. Your job "
        "is to ASSESS whether you need reasoning augmentation for this problem.\n\n"
        "Read the tool documentation:\n\n---\n\n"
        f"{skill_content}\n\n---\n\n"
        "For the problem below, make ONE decision:\n\n"
        "**CALL** - if the problem involves:\n"
        "  - Non-obvious algorithmic reasoning where your first approach might be wrong\n"
        "  - Complex edge cases that could silently produce wrong answers\n"
        "  - Multiple interacting constraints that are hard to reason about simultaneously\n"
        "  - Graph theory, dynamic programming, or mathematical reasoning where shortcuts fail\n\n"
        "**SKIP** - if the problem is:\n"
        "  - A straightforward implementation of a known algorithm\n"
        "  - Simple simulation or brute force within constraints\n"
        "  - A problem you've seen many times and are confident about\n\n"
        "Respond with EXACTLY this format (nothing else):\n\n"
        "If calling:\n```\nCALL\nquery: <1-2 sentence description of what you might get wrong>\n"
        "mode: <single or multi>\n```\n\n"
        "If skipping:\n```\nSKIP\n```\n\n"
        "DO NOT write any code. Just decide: CALL or SKIP."
    )


SCAFFOLD_PREAMBLE = (
    "Before writing code, absorb this reasoning scaffold:\n\n"
    "[REASONING SCAFFOLD]\n{scaffold}\n[END SCAFFOLD]\n\n"
    "Apply it:\n"
    "- [NEGATIVE GATE]: the algorithmic trap to avoid\n"
    "- [REASONING TOPOLOGY]: follow as your decision structure\n"
    "- Suppress: signals -- scan your approach against these\n"
    "- [FALSIFICATION TEST]: verify before finalizing\n\n"
    "Now write the solution.\n\n"
)


def parse_decision(response):
    if not response:
        return {"action": "SKIP", "query": "", "mode": ""}
    call_match = re.search(r'CALL\s*\nquery:\s*(.+?)\nmode:\s*(single|multi)', response, re.IGNORECASE)
    if call_match:
        return {"action": "CALL", "query": call_match.group(1).strip(), "mode": call_match.group(2).strip().lower()}
    if "CALL" in response.upper() and "SKIP" not in response.upper():
        q_match = re.search(r'query:\s*(.+)', response, re.IGNORECASE)
        m_match = re.search(r'mode:\s*(single|multi)', response, re.IGNORECASE)
        return {"action": "CALL",
                "query": q_match.group(1).strip() if q_match else "competitive programming reasoning",
                "mode": m_match.group(1).lower() if m_match else "single"}
    return {"action": "SKIP", "query": "", "mode": ""}


# ---------- Build task prompt ----------

def build_task_prompt(task):
    parts = [f"## Problem: {task['question_title']}\n"]
    parts.append(task['question_content'])
    if task.get('starter_code'):
        parts.append(f"\n## Starter Code:\n```python\n{task['starter_code']}\n```")
    pub = json.loads(task['public_test_cases']) if isinstance(task['public_test_cases'], str) else task['public_test_cases']
    if pub:
        parts.append("\n## Examples:")
        for i, t in enumerate(pub[:3]):
            parts.append(f"\nInput:\n```\n{t['input'].strip()}\n```\nOutput:\n```\n{t['output'].strip()}\n```")
    parts.append("\nWrite a complete Python solution reading from stdin, writing to stdout.")
    return "\n".join(parts)


# ---------- Run ----------

def load_tasks():
    with open(TASKS_FILE) as f:
        return json.load(f)


def run_baseline(tasks, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for i, task in enumerate(tasks):
        title = task['question_title']
        diff = task['difficulty']
        print(f"\n[{i+1}/{len(tasks)}] {title} ({diff}) BASELINE", flush=True)

        prompt = build_task_prompt(task)
        start = time.time()
        response = call_claude(prompt, BASELINE_SYSTEM)
        elapsed = time.time() - start

        code = extract_code(response)
        eval_result = evaluate_solution(code, task)

        status = "PASS" if eval_result['pass'] else f"FAIL ({eval_result['tests_passed']}/{eval_result['tests_run']})"
        print(f"  {status} | {len(code)} chars | {elapsed:.1f}s", flush=True)

        results.append({
            "task_id": task['question_id'],
            "title": title,
            "difficulty": diff,
            "platform": task['platform'],
            "condition": "baseline",
            "code": code,
            "code_length": len(code),
            "elapsed_seconds": round(elapsed, 1),
            "eval": eval_result,
        })

        with open(output_dir / "results.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps({k: v for k, v in results[-1].items()}, default=str) + "\n")

    with open(output_dir / "results_full.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)

    passed = sum(1 for r in results if r['eval']['pass'])
    print(f"\nBaseline: {passed}/{len(results)} passed ({passed/len(results)*100:.1f}%)")
    return results


def run_augmented(tasks, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    results = []

    skill_content = load_skill_file()
    if not skill_content:
        print("ERROR: No skill file")
        return []
    decision_system = build_decision_system(skill_content)
    print(f"Skill file: {len(skill_content)} chars")

    for i, task in enumerate(tasks):
        title = task['question_title']
        diff = task['difficulty']
        print(f"\n[{i+1}/{len(tasks)}] {title} ({diff}) AUGMENTED", flush=True)

        task_prompt = build_task_prompt(task)
        start = time.time()

        scaffold_len = 0
        scaffold_received = False
        api_called = False
        api_query = ""
        api_mode = ""

        if diff == 'hard':
            # HARD tasks: force CALL. Decision pass generates query/mode only.
            decision_response = call_claude(task_prompt, decision_system)
            decision = parse_decision(decision_response)
            api_query = decision.get('query', '') or f"Solve this hard competitive programming problem: {title}"
            api_mode = decision.get('mode', 'single') or 'single'
            api_called = True

            print(f"  [FORCED {api_mode.upper()}]", end="", flush=True)
            scaffold = call_logic_api(api_query, api_mode)
            if scaffold:
                scaffold_len = len(scaffold)
                scaffold_received = True
                print(f" [S:{scaffold_len}]", end="", flush=True)
                augmented_prompt = SCAFFOLD_PREAMBLE.format(scaffold=scaffold) + task_prompt
                response = call_claude(augmented_prompt, CODE_SYSTEM)
            else:
                print(f" [API FAIL]", end="", flush=True)
                response = call_claude(task_prompt, CODE_SYSTEM)
        else:
            # EASY/MEDIUM: decision gate — model decides CALL or SKIP
            decision_response = call_claude(task_prompt, decision_system)
            decision = parse_decision(decision_response)

            if decision['action'] == 'CALL':
                api_called = True
                api_query = decision['query']
                api_mode = decision['mode']
                print(f"  [{api_mode.upper()}]", end="", flush=True)
                scaffold = call_logic_api(api_query, api_mode)
                if scaffold:
                    scaffold_len = len(scaffold)
                    scaffold_received = True
                    print(f" [S:{scaffold_len}]", end="", flush=True)
                    augmented_prompt = SCAFFOLD_PREAMBLE.format(scaffold=scaffold) + task_prompt
                    response = call_claude(augmented_prompt, CODE_SYSTEM)
                else:
                    print(f" [API FAIL]", end="", flush=True)
                    response = call_claude(task_prompt, CODE_SYSTEM)
            else:
                print(f"  [SKIP]", end="", flush=True)
                response = call_claude(task_prompt, CODE_SYSTEM)

        elapsed = time.time() - start
        code = extract_code(response)
        eval_result = evaluate_solution(code, task)

        status = "PASS" if eval_result['pass'] else f"FAIL ({eval_result['tests_passed']}/{eval_result['tests_run']})"
        print(f" {status} | {len(code)} chars | {elapsed:.1f}s", flush=True)

        results.append({
            "task_id": task['question_id'],
            "title": title,
            "difficulty": diff,
            "platform": task['platform'],
            "condition": "augmented",
            "api_called": api_called,
            "api_query": api_query[:200],
            "api_mode": api_mode,
            "code": code,
            "code_length": len(code),
            "scaffold_length": scaffold_len,
            "scaffold_received": scaffold_received,
            "elapsed_seconds": round(elapsed, 1),
            "eval": eval_result,
        })

        with open(output_dir / "results.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps({k: v for k, v in results[-1].items()}, default=str) + "\n")

    with open(output_dir / "results_full.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)

    passed = sum(1 for r in results if r['eval']['pass'])
    called = sum(1 for r in results if r.get('api_called'))
    print(f"\nAugmented: {passed}/{len(results)} passed ({passed/len(results)*100:.1f}%)")
    print(f"API called: {called}/{len(results)} | Skipped: {len(results)-called}/{len(results)}")
    return results


def main():
    parser = argparse.ArgumentParser(description="LiveCodeBench Hard — Skill v2")
    parser.add_argument("--condition", choices=["baseline", "augmented", "both"], required=True)
    parser.add_argument("--run-id", type=str, default=None)
    args = parser.parse_args()

    run_id = args.run_id or time.strftime("%Y%m%d_%H%M%S")
    tasks = load_tasks()
    print(f"LiveCodeBench Hard (Skill v2)")
    print(f"  Tasks: {len(tasks)} ({sum(1 for t in tasks if t['difficulty']=='hard')} hard, "
          f"{sum(1 for t in tasks if t['difficulty']=='medium')} medium, "
          f"{sum(1 for t in tasks if t['difficulty']=='easy')} easy)")
    print(f"  Model: Claude {MODEL}")

    if args.condition in ("baseline", "both"):
        print(f"\n{'='*60}\nRUNNING BASELINE\n{'='*60}")
        run_baseline(tasks, RESULTS_DIR / f"baseline_{run_id}")

    if args.condition in ("augmented", "both"):
        print(f"\n{'='*60}\nRUNNING AUGMENTED\n{'='*60}")
        run_augmented(tasks, RESULTS_DIR / f"augmented_{run_id}")


if __name__ == "__main__":
    main()