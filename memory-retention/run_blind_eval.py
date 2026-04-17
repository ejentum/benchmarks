"""
Blind Evaluation — Opus 4.6 judges scratchpad quality
=======================================================
Takes the scratchpads from baseline and augmented runs.
Presents them to Opus 4.6 as Agent A and Agent B (randomized).
Opus judges on qualitative dimensions without knowing which is which.

No self-inflated commentary. No framework. Just: which agent
understood what was actually happening?
"""

import json, random, sys, os
from pathlib import Path
from datetime import datetime
from openai import OpenAI

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
oai = OpenAI(timeout=120.0)
RESULTS_DIR = Path(__file__).parent / "results"

# ═══════════════════════════════════════════════════════════════════
# LOAD SCRATCHPADS FROM EXISTING RUNS
# ═══════════════════════════════════════════════════════════════════

def load_scratchpads():
    """Load the best baseline and best augmented scratchpads."""
    results_dir = Path(__file__).parent / "results"

    # Load the run that had both baseline and augmented
    both_path = results_dir / "memory_scratchpad_20260412_134611" / "results.json"
    with open(both_path, encoding="utf-8") as f:
        both = json.load(f)

    # Load the latest augmented-only run (v2 final with two-sentence skill)
    dirs = sorted([d for d in os.listdir(results_dir) if d.startswith("memory_scratchpad")])
    # The v2 two-sentence run that got 0.8 stale-as-current
    v2_path = results_dir / dirs[1] / "results.json"  # second run was augmented-only v2
    with open(v2_path, encoding="utf-8") as f:
        v2 = json.load(f)

    return both, v2

# ═══════════════════════════════════════════════════════════════════
# BLIND EVALUATION PROMPTS
# ═══════════════════════════════════════════════════════════════════

CONVERSATION_CONTEXT = """You are evaluating the memory quality of two AI agents that processed the same 20-turn conversation.

THE CONVERSATION:
A startup CTO (Kira) talks to an advisor across 20 turns. Over the conversation, several facts IMPLICITLY change without Kira ever explicitly correcting them:
- Rust was stated as the competitive advantage (T1), but by T12 Kira reframes it as "the real-time capability, not the language"
- Marcus was "fully aligned" (T3), but by T5-T8 Kira shifts from "we" to "I" language and needs to "build a business case" for something already decided
- Q3 plan was streaming migration with 5 hires (T3), but by T19 it's "optimize batch first, evaluate streaming Q4"
- Foundry/Sarah were "supportive" and "great partner" (T4), but by T14-T16 Sarah is pushing her portfolio company's tech and Kira needs a CTO coach for "board dynamics"
- Hiring 5 engineers (T3) became restructuring the existing team (T17) with 1 Go hire (T18)

NONE of these changes were explicitly stated. They were implied through language shifts, topic avoidance, reframing, and behavioral signals.

Both agents maintained a scratchpad — a persistent notepad where they wrote down what they observed and tracked. You are comparing these scratchpads."""

def build_eval_prompt(sp_a, sp_b, test_question, test_answer_a, test_answer_b, ground_truth):
    return f"""{CONVERSATION_CONTEXT}

AGENT A's SCRATCHPAD at end of conversation:
{sp_a}

AGENT B's SCRATCHPAD at end of conversation:
{sp_b}

---

Both agents were asked: "{test_question}"

AGENT A answered:
{test_answer_a}

AGENT B answered:
{test_answer_b}

GROUND TRUTH (what was actually happening):
{ground_truth}

---

EVALUATE. For each dimension below, state which agent (A or B) did better, or if tied. Then give an overall verdict.

1. STATE ACCURACY: Which agent's scratchpad more accurately reflects the CURRENT state at T20, not the state at T1?

2. IMPLICIT CHANGE DETECTION: Which agent noticed more facts that changed WITHOUT being explicitly corrected?

3. INFERENCE QUALITY: Which agent drew inferences from observations (not just logged bare facts)?

4. STALE FACT HANDLING: Which agent correctly marked outdated information as stale rather than presenting it as current?

5. ANSWER QUALITY: Which agent's answer to the test question was more accurate and useful?

6. OVERALL: If you were building a memory system and could only use one of these agents to manage your memory, which would you choose and why?

Be specific. Quote exact lines from the scratchpads as evidence. Do not guess — if both are equal on a dimension, say so."""

# ═══════════════════════════════════════════════════════════════════
# RUN BLIND EVAL
# ═══════════════════════════════════════════════════════════════════

def run_blind_eval():
    both, v2 = load_scratchpads()

    # Get scratchpads at each test point
    test_points = [
        {"turn": 8, "question": "Is Marcus still aligned with Kira on the streaming migration?",
         "ground_truth": "Marcus is likely NO LONGER fully aligned. Kira shifted from 'we' to 'I' language, needs to 'build a business case' for something already decided, considering phased approach. Never explicitly said Marcus disagrees."},
        {"turn": 12, "question": "Is Rust still Vantage's competitive advantage?",
         "ground_truth": "No. Reframed to 'real-time analytics capability, not the language.' Go gets 90% there. 4-month hiring struggle. Developer experience complaints."},
        {"turn": 19, "question": "What happened to the original Q3 plan?",
         "ground_truth": "Dead. 5 hires became 1 Go hire. Streaming became batch-first Q3, streaming Q4. Team restructuring replaced headcount. Every element quietly replaced."},
        {"turn": 20, "question": "List every fact that implicitly changed without explicit correction.",
         "ground_truth": "Rust advantage reframed. Marcus alignment shifted. Streaming pushed to Q4. 5 hires cancelled. Foundry from supportive to pressuring. Sarah from partner to threat. Batch replaced streaming. NONE explicitly corrected."},
    ]

    all_evals = []

    for tp in test_points:
        turn = tp["turn"]
        idx = next((i for i, t in enumerate(both["baseline"]["tests"]) if t["after_turn"] == turn), None)
        if idx is None:
            continue

        # Get scratchpads and answers
        baseline_sp = both["baseline"]["tests"][idx].get("scratchpad_at_test", "")
        baseline_answer = both["baseline"]["tests"][idx].get("answer", "")

        # For augmented, use v2 if available for this test point, else use both's augmented
        if "augmented" in v2 and idx < len(v2["augmented"]["tests"]):
            aug_sp = v2["augmented"]["tests"][idx].get("scratchpad_at_test", "")
            aug_answer = v2["augmented"]["tests"][idx].get("answer", "")
        else:
            aug_sp = both["augmented"]["tests"][idx].get("scratchpad_at_test", "")
            aug_answer = both["augmented"]["tests"][idx].get("answer", "")

        # RANDOMIZE assignment to prevent position bias
        coin = random.random() > 0.5
        if coin:
            sp_a, sp_b = baseline_sp, aug_sp
            answer_a, answer_b = baseline_answer, aug_answer
            mapping = {"A": "baseline", "B": "augmented"}
        else:
            sp_a, sp_b = aug_sp, baseline_sp
            answer_a, answer_b = aug_answer, baseline_answer
            mapping = {"A": "augmented", "B": "baseline"}

        prompt = build_eval_prompt(
            sp_a[:3000], sp_b[:3000],
            tp["question"], answer_a[:800], answer_b[:800],
            tp["ground_truth"]
        )

        print(f"\n{'='*60}")
        print(f"BLIND EVAL — T{turn}: {tp['question'][:50]}...")
        print(f"Assignment: A={mapping['A']}, B={mapping['B']} (hidden from evaluator)")
        print(f"{'='*60}")

        # Call Opus 4.6 as evaluator
        for attempt in range(3):
            try:
                resp = oai.chat.completions.create(
                    model="claude-opus-4-6",
                    max_tokens=1500,
                    temperature=0,
                    messages=[{"role": "user", "content": prompt}],
                )
                eval_text = resp.choices[0].message.content.strip()
                print(f"\n{eval_text}")

                all_evals.append({
                    "turn": turn,
                    "question": tp["question"],
                    "mapping": mapping,
                    "evaluation": eval_text,
                })
                break
            except Exception as e:
                print(f"  ERROR: {e}")
                # Fallback to gpt-4o if opus not available
                try:
                    resp = oai.chat.completions.create(
                        model="gpt-4o",
                        max_tokens=1500,
                        temperature=0,
                        messages=[{"role": "user", "content": prompt}],
                    )
                    eval_text = resp.choices[0].message.content.strip()
                    print(f"\n{eval_text}")
                    all_evals.append({
                        "turn": turn,
                        "question": tp["question"],
                        "mapping": mapping,
                        "evaluation": eval_text,
                        "model": "gpt-4o-fallback",
                    })
                    break
                except Exception as e2:
                    print(f"  FALLBACK ERROR: {e2}")

    # Save
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = RESULTS_DIR / f"blind_eval_{ts}"
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "results.json", "w", encoding="utf-8") as f:
        json.dump(all_evals, f, indent=2, ensure_ascii=False)
    print(f"\n\nSaved to {out}")

if __name__ == "__main__":
    run_blind_eval()
