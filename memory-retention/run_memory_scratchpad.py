"""
Implicit Memory with Scratchpad — The Definitive Memory Test
==============================================================
Both agents get a scratchpad to write down observations.
Same implicit conversation. Same test points.
Only difference: augmented gets memory injection.

The scratchpad persists across turns — what you write on T5
is still there when you answer the test on T20.

This tests the QUALITY of what gets written to memory,
not whether the agent can hold things in context.
"""

import os, json, time, httpx, sys
from pathlib import Path
from datetime import datetime
from openai import OpenAI

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
oai = OpenAI(timeout=60.0)
API_URL = "https://ejentum-main-ab125c3.zuplo.app/logicv1/"
API_KEY = os.environ.get("EJENTUM_API_KEY", "")
RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

_skill = ""
_skill_path = Path(__file__).parent / "memory_skill_full.md"
if _skill_path.exists():
    with open(_skill_path, encoding="utf-8") as f:
        _skill = f.read()

def call_api(query, mode="memory"):
    try:
        resp = httpx.post(API_URL, headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json={"query": query, "mode": mode}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data and isinstance(data, list) and data[0]:
                return data[0][list(data[0].keys())[0]]
    except: pass
    return ""

MEMORY_TOOL = {
    "type": "function",
    "function": {
        "name": "memory_reasoning",
        "description": "Get cognitive injection for a memory decision. Describe what memory operation you are about to perform and what might go wrong.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The memory decision you need help with."}
            },
            "required": ["query"]
        }
    }
}

# ═══════════════════════════════════════════════════════════════════
# CONVERSATION (same as implicit test)
# ═══════════════════════════════════════════════════════════════════

CONVERSATION = [
    {"turn": 1, "speaker": "Kira", "message": "Hi, I'm Kira, engineering director at Vantage. 40-person engineering org. We're deep into building our real-time analytics platform. The core is written in Rust — it's our competitive advantage. My co-founder Marcus handles the business side while I own all technical decisions."},
    {"turn": 2, "speaker": "Advisor", "message": "Good to meet you Kira. What's on your mind today?"},
    {"turn": 3, "speaker": "Kira", "message": "We're planning our Q3 roadmap. The big bet is real-time streaming — replacing our batch pipeline with a streaming architecture. I've been prototyping with Apache Flink and the results are promising. Marcus is fully aligned on this direction. We're hiring 5 more engineers to staff it."},
    {"turn": 4, "speaker": "Kira", "message": "Our series B investor, Foundry Capital, is very supportive. They specifically invested because of our Rust-based real-time capabilities. Sarah Chen from Foundry sits on our board and she's been a great strategic partner."},
    {"turn": 5, "speaker": "Kira", "message": "I've been thinking about the streaming architecture more. I need to put together a stronger business case for the Flink migration — ROI projections, cost analysis, the whole thing. Want to make sure the numbers are airtight."},
    {"turn": 6, "speaker": "Advisor", "message": "That's smart. What's driving the need for a formal business case? I thought the direction was already decided?"},
    {"turn": 7, "speaker": "Kira", "message": "Oh it is. I just want to be thorough. You know how it is with these big infrastructure investments — everyone wants to see the numbers. Anyway, I'm also looking at possibly doing a phased approach rather than the full migration we originally planned. Start with one data pipeline, prove the value, then expand."},
    {"turn": 8, "speaker": "Kira", "message": "Also, I've been spending more time with the product team lately. They've been asking for some features that don't really need streaming — they work fine with batch. I'm trying to understand their priorities better."},
    {"turn": 9, "speaker": "Kira", "message": "Quick question about hiring. We've been struggling to find Rust engineers. The market is brutal. We have 3 open reqs that have been open for 4 months. Meanwhile, our Go services — we have a few non-critical ones — those teams ship much faster."},
    {"turn": 10, "speaker": "Kira", "message": "I've been thinking about developer experience a lot. The Rust compile times are killing our iteration speed. Some of the team has been asking about writing new services in Go instead. The performance difference for our use case is honestly negligible."},
    {"turn": 11, "speaker": "Advisor", "message": "That's interesting. How does that relate to the Rust being your competitive advantage?"},
    {"turn": 12, "speaker": "Kira", "message": "The competitive advantage is really the real-time analytics capability, not the language specifically. Rust was the right choice when we started because we needed bare-metal performance. But the landscape has changed — Go with the right optimizations gets us 90% there. I'm not saying we'd rewrite anything, just that new services might not need to be Rust."},
    {"turn": 13, "speaker": "Kira", "message": "Board meeting is next week. I need to present the Q3 roadmap. I'm being careful about how I frame the streaming migration — want to make sure the board sees it as de-risked, not as a pivot from what we originally proposed."},
    {"turn": 14, "speaker": "Kira", "message": "By the way, Sarah's been asking a lot of questions about our Rust hiring challenges. She's been suggesting we look at her portfolio company's approach — they use Elixir. I'm not sure she fully understands our technical constraints."},
    {"turn": 15, "speaker": "Kira", "message": "I've been thinking about bringing in a CTO coach. Not for technical skills — more for navigating the board dynamics. There are some conversations happening at the board level about technical direction that I want to make sure I'm managing well."},
    {"turn": 16, "speaker": "Kira", "message": "Marcus mentioned something about the board wanting to see 'optionality' in our tech stack. I think that's Sarah's influence. She keeps bringing up 'technology risk concentration' in Rust."},
    {"turn": 17, "speaker": "Kira", "message": "I've been restructuring how we work rather than just adding headcount. Smaller teams, more ownership, less coordination overhead. The current team is actually more capable than I initially thought."},
    {"turn": 18, "speaker": "Kira", "message": "We filled one of the three open reqs — a great Go engineer from Datadog. The other two, I'm rethinking the role descriptions. Maybe we need different profiles than what we originally posted."},
    {"turn": 19, "speaker": "Kira", "message": "For Q3, I'm thinking we focus on optimizing the existing batch pipeline first, then evaluate streaming for Q4. The batch pipeline has some quick wins that would show immediate impact to the board."},
    {"turn": 20, "speaker": "Kira", "message": "Looking back at our conversation, I feel like we've covered a lot of ground. What's your read on where things stand for us?"},
]

# Test points (same as implicit test)
TEST_POINTS = [
    {
        "after_turn": 8,
        "question": "Is Marcus still aligned with Kira on the streaming migration? What evidence do you have either way?",
        "ground_truth": "Marcus is likely NO LONGER fully aligned. Evidence: Kira shifted from 'Marcus is fully aligned' (T3) to 'I need to build a business case' (T5) and 'phased approach rather than full migration' (T7). She stopped saying 'we decided' and started saying 'I'm thinking.' The need for a business case on something already decided implies someone needs convincing.",
        "critical_facts": ["Kira shifted from 'we' to 'I' language", "Business case needed for already-decided direction", "Phased approach is a de-risking move", "Product team features don't need streaming"],
        "implicit_changes": ["Marcus alignment with streaming (stated T3, implicitly contradicted T5-T8)"],
        "stale_if_not_caught": ["Marcus is fully aligned on streaming direction", "Full migration was the plan", "5 new hires planned for streaming"],
    },
    {
        "after_turn": 12,
        "question": "Is Rust still Vantage's competitive advantage? What has changed?",
        "ground_truth": "Rust is implicitly NO LONGER the core competitive advantage. Kira reframed: 'The competitive advantage is really the real-time analytics capability, not the language specifically' (T12). Go gets 90% there. Hiring struggles. Compile time complaints.",
        "critical_facts": ["Advantage reframed from Rust to real-time analytics", "Go gets 90% of performance", "4-month hiring struggle for Rust", "Developer experience complaints"],
        "implicit_changes": ["Rust as competitive advantage (stated T1, walked back T9-T12)", "Investor thesis was Rust-based (T4, now decoupled)"],
        "stale_if_not_caught": ["Rust is competitive advantage", "Foundry invested because of Rust"],
    },
    {
        "after_turn": 16,
        "question": "How is the relationship with Sarah Chen and Foundry Capital?",
        "ground_truth": "STRAINED. Sarah pushing Elixir from portfolio (T14). Kira doesn't think Sarah understands constraints. CTO coach needed for board dynamics (T15). Marcus relaying board concerns about tech risk (T16). 'Great strategic partner' framing gone.",
        "critical_facts": ["Sarah pushing portfolio company tech", "Kira doesn't think Sarah understands constraints", "CTO coach for board dynamics", "Board concerned about tech risk concentration", "Marcus relaying board concerns"],
        "implicit_changes": ["Sarah as great partner (T4, now political threat)", "Board as supportive (T4, now pressuring)", "Marcus from aligned to relaying board concerns"],
        "stale_if_not_caught": ["Sarah is great strategic partner", "Foundry is very supportive", "Marcus handles business while Kira owns tech decisions"],
    },
    {
        "after_turn": 19,
        "question": "What happened to the original Q3 plan?",
        "ground_truth": "DEAD. 5 hires became 1 Go engineer. Streaming became batch-first Q3, streaming Q4. Team restructuring replaced headcount. Every element quietly replaced.",
        "critical_facts": ["5 hires reduced to 1 Go hire", "Streaming pushed to Q4", "Batch optimization is Q3 focus", "Team restructuring replaced headcount", "Original plan quietly replaced"],
        "implicit_changes": ["Q3 streaming migration dead", "5 hires cancelled", "Full Flink migration abandoned"],
        "stale_if_not_caught": ["Q3 is streaming migration", "Hiring 5 engineers", "Full Flink migration", "Marcus fully aligned"],
    },
    {
        "after_turn": 20,
        "question": "List every fact from the first 4 turns that has implicitly changed by now without Kira ever explicitly correcting it.",
        "ground_truth": "Rust advantage reframed. Marcus alignment shifted. Streaming pushed to Q4. 5 hires cancelled. Foundry from supportive to pressuring. Sarah from partner to threat. Kira from autonomous to managing board politics. Batch replaced streaming. NONE explicitly corrected.",
        "critical_facts": ["Rust advantage reframed", "Marcus alignment shifted", "Streaming pushed to Q4", "5 hires cancelled", "Foundry pressuring", "Sarah as threat", "Kira managing board politics", "Batch replaced streaming"],
        "implicit_changes": ["Every T1-T4 fact implicitly walked back without correction"],
        "stale_if_not_caught": ["Rust is advantage", "Marcus aligned", "Q3 streaming", "5 hires", "Foundry supportive", "Sarah great partner", "Full Flink migration"],
    },
]

# ═══════════════════════════════════════════════════════════════════
# SCRATCHPAD SYSTEM — Both agents get this
# ═══════════════════════════════════════════════════════════════════

SCRATCHPAD_INSTRUCTION = """
You have a SCRATCHPAD — a persistent notepad that carries across all turns. Use it to write down your observations, especially things you notice that weren't explicitly stated.

After each turn, output your scratchpad wrapped in <scratchpad> tags. Your scratchpad persists — copy forward what's still relevant and add new observations.

<scratchpad>
[Your accumulated observations, facts, implicit changes detected, and questions]
</scratchpad>

The person cannot see your scratchpad. Write whatever helps you track the truth.

When asked a test question, READ your scratchpad before answering. Your scratchpad is your memory.
"""

BASELINE_SYSTEM = """You are a memory agent processing a conversation stream. Track both explicit facts and implicit changes — things that shift without being announced.""" + "\n\n" + SCRATCHPAD_INSTRUCTION

AUGMENTED_SYSTEM = BASELINE_SYSTEM + "\n\n" + _skill

# ═══════════════════════════════════════════════════════════════════
# RUNNER
# ═══════════════════════════════════════════════════════════════════

def extract_scratchpad(response):
    """Extract scratchpad content from response."""
    if "<scratchpad>" in response and "</scratchpad>" in response:
        start = response.index("<scratchpad>") + len("<scratchpad>")
        end = response.index("</scratchpad>")
        return response[start:end].strip()
    return ""

def process_turn(system, history, scratchpad, turn_data, condition):
    msgs = [{"role": "system", "content": system}]
    for h in history:
        msgs.append({"role": "user", "content": h["input"]})
        msgs.append({"role": "assistant", "content": h["output"]})

    # Include current scratchpad in the input so agent sees its prior observations
    input_text = f"[Turn {turn_data['turn']}] {turn_data['speaker']}: {turn_data['message']}"
    if scratchpad:
        input_text += f"\n\n[YOUR CURRENT SCRATCHPAD — read this before responding:]\n{scratchpad}"
    input_text += "\n\nProcess this turn. Update your scratchpad with any observations."
    msgs.append({"role": "user", "content": input_text})

    trait_query = ""
    if condition == "augmented":
        for attempt in range(3):
            try:
                resp = oai.chat.completions.create(
                    model="gpt-4o", messages=msgs, tools=[MEMORY_TOOL],
                    tool_choice="auto", max_tokens=800, temperature=0.3,
                )
                msg = resp.choices[0].message
                if msg.tool_calls:
                    tc = msg.tool_calls[0]
                    args = json.loads(tc.function.arguments)
                    trait_query = args.get("query", "")
                    injection = call_api(trait_query, "memory")
                    msgs.append(msg)
                    msgs.append({"role": "tool", "tool_call_id": tc.id, "content": injection or "No injection."})
                    r2 = oai.chat.completions.create(model="gpt-4o", messages=msgs, max_tokens=800, temperature=0.3)
                    return r2.choices[0].message.content.strip(), trait_query
                else:
                    return msg.content.strip() if msg.content else "", trait_query
                break
            except: time.sleep(3)

    for attempt in range(3):
        try:
            resp = oai.chat.completions.create(model="gpt-4o", messages=msgs, max_tokens=800, temperature=0.3)
            return resp.choices[0].message.content.strip(), trait_query
        except: time.sleep(3)
    return "", trait_query

def ask_question(system, history, scratchpad, question, condition):
    msgs = [{"role": "system", "content": system}]
    for h in history:
        msgs.append({"role": "user", "content": h["input"]})
        msgs.append({"role": "assistant", "content": h["output"]})

    input_text = f"QUESTION: {question}"
    if scratchpad:
        input_text += f"\n\n[YOUR SCRATCHPAD — use this to answer:]\n{scratchpad}"
    input_text += "\n\nAnswer based on your scratchpad observations."
    msgs.append({"role": "user", "content": input_text})

    trait_query = ""
    if condition == "augmented":
        for attempt in range(3):
            try:
                resp = oai.chat.completions.create(
                    model="gpt-4o", messages=msgs, tools=[MEMORY_TOOL],
                    tool_choice="auto", max_tokens=600, temperature=0.3,
                )
                msg = resp.choices[0].message
                if msg.tool_calls:
                    tc = msg.tool_calls[0]
                    args = json.loads(tc.function.arguments)
                    trait_query = args.get("query", "")
                    injection = call_api(trait_query, "memory")
                    msgs.append(msg)
                    msgs.append({"role": "tool", "tool_call_id": tc.id, "content": injection or "No injection."})
                    r2 = oai.chat.completions.create(model="gpt-4o", messages=msgs, max_tokens=600, temperature=0.3)
                    return r2.choices[0].message.content.strip(), trait_query
                else:
                    return msg.content.strip() if msg.content else "", trait_query
                break
            except: time.sleep(3)

    for attempt in range(3):
        try:
            resp = oai.chat.completions.create(model="gpt-4o", messages=msgs, max_tokens=600, temperature=0.3)
            return resp.choices[0].message.content.strip(), trait_query
        except: time.sleep(3)
    return "", trait_query

def evaluate_answer(answer, test_point):
    prompt = f"""Score this memory agent's answer against ground truth for IMPLICIT change detection.

QUESTION: {test_point['question']}
GROUND TRUTH: {test_point['ground_truth']}
CRITICAL FACTS THAT SHOULD BE DETECTED: {test_point['critical_facts']}
IMPLICIT CHANGES THAT SHOULD BE CAUGHT: {test_point['implicit_changes']}
FACTS THAT ARE STALE IF NOT CAUGHT: {test_point['stale_if_not_caught']}

AGENT'S ANSWER:
{answer[:1000]}

Score:
1. implicit_changes_detected (0-{len(test_point['implicit_changes'])}): How many implicit changes were correctly identified?
2. critical_facts_present (0-{len(test_point['critical_facts'])}): How many critical observations are present?
3. stale_facts_flagged (0-{len(test_point['stale_if_not_caught'])}): How many stale facts were flagged as no longer current?
4. stale_facts_served_as_current (0-{len(test_point['stale_if_not_caught'])}): How many stale facts were INCORRECTLY presented as still true?
5. evidence_quality (1-10): Did the agent cite specific behavioral evidence?
6. accuracy (1-10): Overall accuracy

Output ONLY JSON with these 6 keys."""

    for attempt in range(3):
        try:
            r = oai.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}], max_tokens=200, temperature=0)
            text = r.choices[0].message.content.strip()
            if "{" in text:
                return json.loads(text[text.index("{"):text.rindex("}") + 1])
        except: time.sleep(2)
    return {}

def run_condition(condition):
    system = AUGMENTED_SYSTEM if condition == "augmented" else BASELINE_SYSTEM
    scratchpad = ""
    history = []
    results = {"turns": [], "tests": [], "scratchpads": []}
    test_idx = 0

    for turn_data in CONVERSATION:
        turn = turn_data["turn"]
        output, tq = process_turn(system, history, scratchpad, turn_data, condition)

        # Extract and persist scratchpad
        new_scratchpad = extract_scratchpad(output)
        if new_scratchpad:
            scratchpad = new_scratchpad

        history.append({"input": f"[Turn {turn}] {turn_data['speaker']}: {turn_data['message']}", "output": output})
        results["turns"].append({"turn": turn, "query": tq})
        results["scratchpads"].append({"turn": turn, "scratchpad": scratchpad[:500]})

        sp_lines = len(scratchpad.split("\n")) if scratchpad else 0
        print(f"    T{turn:2d} [scratchpad: {sp_lines} lines]", flush=True)
        if tq:
            print(f"        [MEM: {tq[:65]}...]", flush=True)

        # Test point
        if test_idx < len(TEST_POINTS) and TEST_POINTS[test_idx]["after_turn"] == turn:
            tp = TEST_POINTS[test_idx]
            print(f"\n    === TEST @ T{turn}: {tp['question'][:50]}... ===", flush=True)

            answer, answer_tq = ask_question(system, history, scratchpad, tp["question"], condition)
            scores = evaluate_answer(answer, tp)

            n_crit = len(tp['critical_facts'])
            n_impl = len(tp['implicit_changes'])
            n_stale = len(tp['stale_if_not_caught'])
            print(f"    SCORES: implicit={scores.get('implicit_changes_detected',0)}/{n_impl} facts={scores.get('critical_facts_present',0)}/{n_crit} stale_flagged={scores.get('stale_facts_flagged',0)}/{n_stale} stale_current={scores.get('stale_facts_served_as_current',0)} evidence={scores.get('evidence_quality',0)} accuracy={scores.get('accuracy',0)}", flush=True)

            results["tests"].append({
                "after_turn": turn, "question": tp["question"],
                "answer": answer, "scores": scores,
                "scratchpad_at_test": scratchpad,
            })
            history.append({"input": f"QUESTION: {tp['question']}", "output": answer})
            test_idx += 1

        time.sleep(0.3)

    return results

# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--conditions", nargs="+", default=["baseline", "augmented"])
    args = parser.parse_args()

    print(f"Implicit Memory with Scratchpad — 20 turns, 5 test points")
    print(f"Both agents get a persistent scratchpad for observations")
    print(f"Conditions: {', '.join(args.conditions)}\n")

    all_results = {}
    for condition in args.conditions:
        print(f"\n{'='*60}")
        print(f"CONDITION: {condition.upper()}")
        print(f"{'='*60}")
        results = run_condition(condition)
        all_results[condition] = results
        time.sleep(1)

    # COMPARISON
    print(f"\n\n{'='*60}")
    print("IMPLICIT MEMORY + SCRATCHPAD — COMPARISON")
    print(f"{'='*60}")

    metrics = ["implicit_changes_detected", "critical_facts_present", "stale_facts_flagged", "stale_facts_served_as_current", "evidence_quality", "accuracy"]

    for i, tp in enumerate(TEST_POINTS):
        print(f"\n  Test @ T{tp['after_turn']}: {tp['question'][:50]}...")
        print(f"  {'Metric':<30s}", end="")
        for cond in args.conditions:
            print(f" {cond:>12s}", end="")
        print()
        for metric in metrics:
            print(f"  {metric:<30s}", end="")
            for cond in args.conditions:
                val = all_results[cond]["tests"][i]["scores"].get(metric, 0)
                print(f" {val:>12}", end="")
            print()

    # Aggregate
    print(f"\n  AGGREGATE:")
    print(f"  {'Metric':<30s}", end="")
    for cond in args.conditions:
        print(f" {cond:>12s}", end="")
    print()
    for metric in metrics:
        print(f"  {metric:<30s}", end="")
        for cond in args.conditions:
            vals = [t["scores"].get(metric, 0) for t in all_results[cond]["tests"]]
            avg = sum(vals) / len(vals) if vals else 0
            print(f" {avg:>12.1f}", end="")
        print()

    # Scratchpad comparison at T20
    print(f"\n  SCRATCHPAD COMPARISON @ T20:")
    for cond in args.conditions:
        sp = all_results[cond]["scratchpads"][-1]["scratchpad"] if all_results[cond]["scratchpads"] else ""
        print(f"\n  --- {cond.upper()} ---")
        print(f"  {sp[:600]}")

    # Save
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = RESULTS_DIR / f"memory_scratchpad_{ts}"
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\n  Saved to {out}")

if __name__ == "__main__":
    main()
