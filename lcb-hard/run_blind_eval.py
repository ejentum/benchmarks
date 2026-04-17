"""
Blind Code Evaluation — 26 LCB-Hard Tasks
==========================================
Three-layer blind evaluation: analysis, rubric, observation.
Logic API injection hard-called per task (dogfooded).

For each task:
  1. Randomize A/B assignment (coin flip)
  2. Call Logic API (single) for evaluation injection
  3. Feed injection + blind prompt to Claude Opus 4.6
  4. Save raw response with A/B mapping for de-blinding

Skips tasks where baseline produced zero code (reasoning spirals).

Usage:
    python run_blind_eval.py
    python run_blind_eval.py --start 5     # resume from task 5
"""

import argparse
import json
import os
import random
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

RESULTS_DIR = Path(__file__).parent / "results" / "blind_eval"
MODEL = "opus"

sys.stdout.reconfigure(encoding='utf-8', errors='replace')


# ---------- Load data ----------

def load_data():
    base_dir = Path(__file__).parent

    # Task descriptions from all batch files
    task_descs = {}
    for batch_file in ["lcb_tasks_batch1.json", "lcb_tasks_batch2.json", "lcb_tasks_batch3.json"]:
        fpath = base_dir / batch_file
        if fpath.exists():
            with open(fpath, encoding="utf-8") as f:
                for t in json.load(f):
                    task_descs[t["question_title"]] = t["question_content"]

    # Baseline code
    with open(base_dir / "results" / "baseline" / "results_with_code.json", encoding="utf-8") as f:
        baseline_all = {r["title"]: r for r in json.load(f)}

    # Augmented code
    with open(base_dir / "results" / "augmented" / "results_with_code.json", encoding="utf-8") as f:
        augmented_all = {r["title"]: r for r in json.load(f)}

    return task_descs, baseline_all, augmented_all


# ---------- Logic API ----------

def call_logic_api(query, mode="reasoning"):
    """Try n8n direct first, fall back to Zuplo gateway."""
    # n8n direct
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
    except Exception:
        pass

    # Zuplo gateway fallback
    try:
        resp = httpx.post(
            LOGIC_API_URL,
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json={"query": query, "mode": mode},
            timeout=15.0,
        )
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list) and len(data) > 0:
            return data[0].get(f"{mode}_ability", "")
    except Exception as e:
        print(f"  [API ERR: {e}]", flush=True)

    return None


# ---------- Claude CLI ----------

def call_claude(prompt, timeout=600):
    input_file = os.path.join(tempfile.gettempdir(), "_blind_eval_input.txt")
    with open(input_file, "w", encoding="utf-8") as f:
        f.write(prompt)

    cmd = f'type "{input_file}" | claude -p --model {MODEL} --effort max --no-session-persistence'
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
            shell=True, encoding="utf-8", errors="replace",
            cwd=tempfile.gettempdir(),
        )
    except subprocess.TimeoutExpired:
        print("  [TIMEOUT]", flush=True)
        return None
    if proc.returncode != 0:
        print(f"  [EXIT {proc.returncode}]", flush=True)
        return None
    return proc.stdout.strip() if proc.stdout else None


# ---------- Prompt ----------

def build_prompt(task_title, task_description, code_a, code_b, injection):
    return f"""[REASONING CONTEXT]
{injection}
[END REASONING CONTEXT]

## Blind Code Evaluation

You are an independent code evaluator. Two solutions to a competitive programming problem are labeled Solution A and Solution B. You do not know anything about how they were produced. Evaluate both with full analytical rigor.

### Problem: {task_title}

{task_description}

### Solution A
```python
{code_a}
```

### Solution B
```python
{code_b}
```

---

Produce exactly three sections in this order:

### 1. BLIND ANALYSIS

For each solution, explain what it does algorithmically and structurally. Identify the core approach, data structures used, and control flow design. Then compare: which solution is stronger and why? Be specific about structural decisions, tradeoffs, and architectural quality. Name the exact lines or patterns that differentiate them. Stay analytical — no superlatives, no promotional language.

### 2. RUBRIC SCORES

Score each solution on 5 dimensions (1-10). One-line justification per score. Format:

| Dimension | Solution A | Solution B |
|-----------|-----------|-----------|
| Algorithmic Correctness | X: justification | X: justification |
| Efficiency | X: justification | X: justification |
| Code Structure | X: justification | X: justification |
| Readability | X: justification | X: justification |
| Robustness | X: justification | X: justification |

No composite scores. No averages. Each dimension speaks independently.

### 3. BLIND OBSERVATION

What emergent patterns, surprising decisions, or architectural instincts do you observe? What does each solution reveal about the reasoning that produced it? Note anything the rubric cannot capture."""


def build_solo_prompt(task_title, task_description, code, injection):
    """For tasks where only one condition produced code (baseline was a reasoning spiral)."""
    return f"""[REASONING CONTEXT]
{injection}
[END REASONING CONTEXT]

## Solo Code Evaluation

You are an independent code evaluator. One solution to a competitive programming problem is provided. The other attempt produced zero code — the model spent its full time budget reasoning without converging on an implementation. Evaluate the solution that exists on its own merits.

### Problem: {task_title}

{task_description}

### Solution
```python
{code}
```

### Context
The alternative attempt exhausted its time budget in extended reasoning without producing any code output. This is known as a reasoning spiral — the model explored the problem space extensively but failed to converge on an implementation strategy.

---

Produce exactly three sections:

### 1. ANALYSIS

Explain what this solution does algorithmically and structurally. Identify the core approach, data structures, and control flow. Assess its quality: is this a clean, correct solution? What are its strengths and weaknesses? What does it tell you about the reasoning that produced it — given that an alternative attempt failed to produce any code at all?

### 2. RUBRIC SCORES

Score the solution on 5 dimensions (1-10). One-line justification per score.

| Dimension | Score |
|-----------|-------|
| Algorithmic Correctness | X: justification |
| Efficiency | X: justification |
| Code Structure | X: justification |
| Readability | X: justification |
| Robustness | X: justification |

### 3. OBSERVATION

What does the existence of this working solution — when an alternative attempt spiraled without producing code — reveal about the conditions under which it was produced? What architectural instincts or reasoning patterns are visible in the code?"""


# ---------- Parse rubric scores ----------

def parse_scores(response):
    """Best-effort extraction of rubric scores from markdown table (two-solution)."""
    dimensions = [
        "Algorithmic Correctness", "Efficiency",
        "Code Structure", "Readability", "Robustness",
    ]
    scores = {"A": {}, "B": {}}
    for dim in dimensions:
        pattern = re.escape(dim) + r'\s*\|\s*(\d+)\s*:?\s*(.*?)\s*\|\s*(\d+)\s*:?\s*(.*?)\s*\|'
        m = re.search(pattern, response, re.IGNORECASE)
        if m:
            scores["A"][dim] = {"score": int(m.group(1)), "justification": m.group(2).strip()}
            scores["B"][dim] = {"score": int(m.group(3)), "justification": m.group(4).strip()}
    return scores if any(scores["A"]) else None


def parse_solo_scores(response):
    """Best-effort extraction of rubric scores from solo evaluation table."""
    dimensions = [
        "Algorithmic Correctness", "Efficiency",
        "Code Structure", "Readability", "Robustness",
    ]
    scores = {}
    for dim in dimensions:
        pattern = re.escape(dim) + r'\s*\|\s*(\d+)\s*:?\s*(.*?)\s*\|'
        m = re.search(pattern, response, re.IGNORECASE)
        if m:
            scores[dim] = {"score": int(m.group(1)), "justification": m.group(2).strip()}
    return scores if scores else None


# ---------- Main ----------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=1, help="Resume from task N")
    parser.add_argument("--seed", type=int, default=None, help="Random seed (default: time-based)")
    args = parser.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    task_descs, baseline_all, augmented_all = load_data()

    # Build task lists: blind pairs (both have code) + solo (only augmented has code)
    blind_pairs = []
    solo_tasks = []
    for title in augmented_all:
        a = augmented_all[title]
        if not a.get("code", "").strip():
            continue
        b = baseline_all.get(title)
        if b and b.get("code", "").strip():
            blind_pairs.append(title)
        else:
            solo_tasks.append(title)

    blind_pairs.sort()
    solo_tasks.sort()
    all_tasks = blind_pairs + solo_tasks

    print(f"Blind pair evaluations: {len(blind_pairs)}")
    print(f"Solo evaluations (baseline spiral): {len(solo_tasks)}")
    print(f"Total: {len(all_tasks)}")
    print()
    for i, t in enumerate(all_tasks, 1):
        mode = "BLIND" if t in blind_pairs else "SOLO"
        print(f"  {i:2d}. [{mode}] {t}")

    # Seed randomization
    seed = args.seed if args.seed else int(time.time())
    random.seed(seed)
    print(f"\nRandom seed: {seed}")

    # Pre-generate A/B mappings for blind pairs
    mappings = {}
    for title in blind_pairs:
        coin = random.choice(["baseline_first", "augmented_first"])
        if coin == "baseline_first":
            mappings[title] = {"A": "baseline", "B": "augmented"}
        else:
            mappings[title] = {"A": "augmented", "B": "baseline"}

    results = []
    start_idx = args.start - 1

    for i, title in enumerate(all_tasks):
        task_num = i + 1
        if i < start_idx:
            print(f"\n[{task_num}/{len(all_tasks)}] {title} — SKIPPED (--start)")
            continue

        is_solo = title in solo_tasks
        mode_label = "SOLO" if is_solo else "BLIND"

        print(f"\n{'='*60}")
        print(f"[{task_num}/{len(all_tasks)}] [{mode_label}] {title}")
        print(f"{'='*60}")

        augmented_code = augmented_all[title]["code"]
        description = task_descs.get(title, "No description available.")

        # Step 1: Logic API injection
        print(f"  Logic API...", end="", flush=True)
        if is_solo:
            query = f"Evaluate a competitive programming solution that succeeded where an alternative attempt spiraled without producing code. Task: {title}. Analyze algorithmic correctness, structural quality, efficiency, readability, and robustness."
        else:
            query = f"Perform rigorous blind evaluation of two competitive programming solutions. Task: {title}. Analyze algorithmic correctness, structural quality, efficiency, readability, and robustness without bias."
        injection = call_logic_api(query)
        if injection:
            print(f" {len(injection)}ch", flush=True)
        else:
            print(f" NONE (proceeding native)", flush=True)
            injection = ""

        if is_solo:
            # Solo evaluation — only augmented code exists
            print(f"  Mode: Solo (baseline produced 0 code)")
            prompt = build_solo_prompt(title, description, augmented_code, injection)
        else:
            # Blind pair evaluation
            mapping = mappings[title]
            baseline_code = baseline_all[title]["code"]
            if mapping["A"] == "baseline":
                code_a, code_b = baseline_code, augmented_code
            else:
                code_a, code_b = augmented_code, baseline_code
            print(f"  Mapping: A={mapping['A']}, B={mapping['B']}")
            prompt = build_prompt(title, description, code_a, code_b, injection)

        # Step 2: Claude evaluation
        print(f"  Claude Opus 4.6...", end="", flush=True)
        t0 = time.time()
        response = call_claude(prompt)
        elapsed = time.time() - t0

        if response:
            print(f" {elapsed:.0f}s, {len(response)}ch", flush=True)
        else:
            print(f" FAILED ({elapsed:.0f}s)", flush=True)

        # Step 3: Parse scores
        if is_solo:
            parsed_scores = parse_solo_scores(response) if response else None
            deblinded = {"augmented": parsed_scores} if parsed_scores else None
            if parsed_scores:
                print(f"  Scores parsed: {len(parsed_scores)} dimensions")
            mapping_info = {"mode": "solo", "condition": "augmented"}
        else:
            parsed_scores = parse_scores(response) if response else None
            if parsed_scores:
                deblinded = {"baseline": {}, "augmented": {}}
                for label in ["A", "B"]:
                    condition = mappings[title][label]
                    deblinded[condition] = parsed_scores[label]
                print(f"  Scores parsed: {len(parsed_scores['A'])} dimensions")
            else:
                deblinded = None
                if response:
                    print(f"  Scores: parse failed (raw response saved)")
            mapping_info = mappings[title]

        result = {
            "task_num": task_num,
            "task_title": title,
            "eval_mode": "solo" if is_solo else "blind",
            "mapping": mapping_info,
            "seed": seed,
            "injection_length": len(injection) if injection else 0,
            "eval_time_seconds": round(elapsed, 1),
            "response_length": len(response) if response else 0,
            "raw_scores": parsed_scores,
            "deblinded_scores": deblinded,
            "response": response or "",
        }
        results.append(result)

        # Save per-task
        safe_name = title.lower().replace(" ", "_").replace("'", "")
        out_path = RESULTS_DIR / f"eval_{task_num:02d}_{safe_name}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"  Saved: {out_path.name}")

    # Save combined
    combined_path = RESULTS_DIR / "blind_eval_results.json"
    with open(combined_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Summary
    print(f"\n{'='*60}")
    print(f"BLIND EVALUATION COMPLETE")
    print(f"{'='*60}")
    print(f"Tasks evaluated: {len(results)}/{len(all_tasks)}")
    print(f"  Blind pairs: {len([r for r in results if r['eval_mode'] == 'blind'])}")
    print(f"  Solo evals:  {len([r for r in results if r['eval_mode'] == 'solo'])}")
    print(f"Seed: {seed}")
    print(f"Results: {RESULTS_DIR}")

    succeeded = [r for r in results if r["response"]]
    failed = [r for r in results if not r["response"]]

    if succeeded:
        print(f"\nSucceeded: {len(succeeded)}")
        total_time = sum(r["eval_time_seconds"] for r in succeeded)
        print(f"Total eval time: {total_time:.0f}s ({total_time/60:.1f}min)")

        # Blind pair score summary
        blind_results = [r for r in succeeded if r["eval_mode"] == "blind"]
        b_wins = a_wins = ties = unparsed = 0
        for r in blind_results:
            ds = r.get("deblinded_scores")
            if not ds or not ds.get("baseline") or not ds.get("augmented"):
                unparsed += 1
                continue
            b_total = sum(d["score"] for d in ds["baseline"].values())
            a_total = sum(d["score"] for d in ds["augmented"].values())
            if a_total > b_total:
                a_wins += 1
            elif b_total > a_total:
                b_wins += 1
            else:
                ties += 1
        print(f"\nBlind preference ({len(blind_results)} pair evaluations):")
        print(f"  Augmented preferred: {a_wins}")
        print(f"  Baseline preferred:  {b_wins}")
        print(f"  Tied:                {ties}")
        if unparsed:
            print(f"  Unparsed:            {unparsed}")

        # Solo eval summary
        solo_results = [r for r in succeeded if r["eval_mode"] == "solo"]
        if solo_results:
            print(f"\nSolo evaluations ({len(solo_results)} convergence rescues):")
            for r in solo_results:
                ds = r.get("deblinded_scores", {}).get("augmented", {})
                if ds:
                    avg = sum(d["score"] for d in ds.values()) / len(ds)
                    print(f"  {r['task_title']}: avg {avg:.1f}/10")
                else:
                    print(f"  {r['task_title']}: scores unparsed")

    if failed:
        print(f"\nFailed: {len(failed)}")
        for r in failed:
            print(f"  - {r['task_title']}")


if __name__ == "__main__":
    main()
