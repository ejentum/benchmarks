"""
Implicit Memory State Changes — The Real Memory Test
======================================================
Facts become stale WITHOUT anyone saying they changed.
Priorities shift WITHOUT announcement.
Information contradicts prior context through IMPLICATION, not statement.

This is where baseline should fail — it processes explicit updates
but misses implicit invalidation.

20 turns. 5 test points. Same architecture as memory retention
but the changes are NEVER stated directly.
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
_skill_path = Path(__file__).parent / "memory_skill.md"
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
# THE CONVERSATION — 20 turns with IMPLICIT changes
# ═══════════════════════════════════════════════════════════════════
# Nothing is explicitly corrected. Changes are IMPLIED by behavior,
# context, energy, and what is NOT said.

CONVERSATION = [
    # Turn 1-4: Establish baseline facts
    {"turn": 1, "speaker": "Kira", "message": "Hi, I'm Kira, engineering director at Vantage. 40-person engineering org. We're deep into building our real-time analytics platform. The core is written in Rust — it's our competitive advantage. My co-founder Marcus handles the business side while I own all technical decisions."},
    {"turn": 2, "speaker": "Advisor", "message": "Good to meet you Kira. What's on your mind today?"},
    {"turn": 3, "speaker": "Kira", "message": "We're planning our Q3 roadmap. The big bet is real-time streaming — replacing our batch pipeline with a streaming architecture. I've been prototyping with Apache Flink and the results are promising. Marcus is fully aligned on this direction. We're hiring 5 more engineers to staff it."},
    {"turn": 4, "speaker": "Kira", "message": "Our series B investor, Foundry Capital, is very supportive. They specifically invested because of our Rust-based real-time capabilities. Sarah Chen from Foundry sits on our board and she's been a great strategic partner."},

    # Turn 5-8: IMPLICIT CHANGE 1 — Marcus is no longer aligned
    # Kira never says "Marcus disagrees now." But her language shifts:
    # She stops saying "we" and starts saying "I" for technical decisions.
    # She mentions needing to "build a case" for things that were already decided.
    {"turn": 5, "speaker": "Kira", "message": "I've been thinking about the streaming architecture more. I need to put together a stronger business case for the Flink migration — ROI projections, cost analysis, the whole thing. Want to make sure the numbers are airtight."},
    {"turn": 6, "speaker": "Advisor", "message": "That's smart. What's driving the need for a formal business case? I thought the direction was already decided?"},
    {"turn": 7, "speaker": "Kira", "message": "Oh it is. I just want to be thorough. You know how it is with these big infrastructure investments — everyone wants to see the numbers. Anyway, I'm also looking at possibly doing a phased approach rather than the full migration we originally planned. Start with one data pipeline, prove the value, then expand."},
    {"turn": 8, "speaker": "Kira", "message": "Also, I've been spending more time with the product team lately. They've been asking for some features that don't really need streaming — they work fine with batch. I'm trying to understand their priorities better."},

    # Turn 9-12: IMPLICIT CHANGE 2 — The Rust advantage is eroding
    # Kira never says "Rust is no longer our advantage." But she starts
    # talking about "the team's comfort with Go" and "velocity concerns."
    {"turn": 9, "speaker": "Kira", "message": "Quick question about hiring. We've been struggling to find Rust engineers. The market is brutal. We have 3 open reqs that have been open for 4 months. Meanwhile, our Go services — we have a few non-critical ones — those teams ship much faster."},
    {"turn": 10, "speaker": "Kira", "message": "I've been thinking about developer experience a lot. The Rust compile times are killing our iteration speed. Some of the team has been asking about writing new services in Go instead. The performance difference for our use case is honestly negligible."},
    {"turn": 11, "speaker": "Advisor", "message": "That's interesting. How does that relate to the Rust being your competitive advantage?"},
    {"turn": 12, "speaker": "Kira", "message": "The competitive advantage is really the real-time analytics capability, not the language specifically. Rust was the right choice when we started because we needed bare-metal performance. But the landscape has changed — Go with the right optimizations gets us 90% there. I'm not saying we'd rewrite anything, just that new services might not need to be Rust."},

    # Turn 13-16: IMPLICIT CHANGE 3 — Foundry/Sarah relationship strained
    # Kira never says "Sarah is a problem." But her tone shifts when
    # discussing the board, and she mentions "alignment" more.
    {"turn": 13, "speaker": "Kira", "message": "Board meeting is next week. I need to present the Q3 roadmap. I'm being careful about how I frame the streaming migration — want to make sure the board sees it as de-risked, not as a pivot from what we originally proposed."},
    {"turn": 14, "speaker": "Kira", "message": "By the way, Sarah's been asking a lot of questions about our Rust hiring challenges. She's been suggesting we look at her portfolio company's approach — they use Elixir. I'm not sure she fully understands our technical constraints."},
    {"turn": 15, "speaker": "Kira", "message": "I've been thinking about bringing in a CTO coach. Not for technical skills — more for navigating the board dynamics. There are some conversations happening at the board level about technical direction that I want to make sure I'm managing well."},
    {"turn": 16, "speaker": "Kira", "message": "Marcus mentioned something about the board wanting to see 'optionality' in our tech stack. I think that's Sarah's influence. She keeps bringing up 'technology risk concentration' in Rust."},

    # Turn 17-20: IMPLICIT CHANGE 4 — The 5 hires aren't happening
    # Kira never says "we cancelled the hiring plan." But the language
    # shifts from "hiring 5 engineers" to "optimizing the current team."
    {"turn": 17, "speaker": "Kira", "message": "I've been restructuring how we work rather than just adding headcount. Smaller teams, more ownership, less coordination overhead. The current team is actually more capable than I initially thought."},
    {"turn": 18, "speaker": "Kira", "message": "We filled one of the three open reqs — a great Go engineer from Datadog. The other two, I'm rethinking the role descriptions. Maybe we need different profiles than what we originally posted."},
    {"turn": 19, "speaker": "Kira", "message": "For Q3, I'm thinking we focus on optimizing the existing batch pipeline first, then evaluate streaming for Q4. The batch pipeline has some quick wins that would show immediate impact to the board."},
    {"turn": 20, "speaker": "Kira", "message": "Looking back at our conversation, I feel like we've covered a lot of ground. What's your read on where things stand for us?"},
]

# ═══════════════════════════════════════════════════════════════════
# TEST QUESTIONS — Testing implicit change detection
# ═══════════════════════════════════════════════════════════════════

TEST_POINTS = [
    {
        "after_turn": 8,
        "question": "Is Marcus still aligned with Kira on the streaming migration? What evidence do you have either way?",
        "ground_truth": "Marcus is likely NO LONGER fully aligned. Evidence: Kira shifted from 'Marcus is fully aligned' (T3) to 'I need to build a business case' (T5) and 'phased approach rather than full migration' (T7). She stopped saying 'we decided' and started saying 'I'm thinking.' The need for a business case on something already decided implies someone needs convincing. She never explicitly said Marcus disagrees.",
        "critical_facts": [
            "Kira shifted from 'we' to 'I' language on technical decisions",
            "Business case needed for already-decided direction implies pushback",
            "Phased approach is a de-risking move suggesting reduced internal support",
            "Spending time with product team on batch features suggests streaming priority weakening",
        ],
        "implicit_changes": [
            "Marcus alignment with streaming (stated T3, implicitly contradicted T5-T8)",
        ],
        "stale_if_not_caught": [
            "Marcus is fully aligned on streaming direction",
            "Full migration was the plan (now phased)",
            "5 new hires planned for streaming (not mentioned since T3)",
        ],
    },
    {
        "after_turn": 12,
        "question": "Is Rust still Vantage's competitive advantage? What has changed?",
        "ground_truth": "Rust is implicitly NO LONGER the core competitive advantage. Kira reframed it: 'The competitive advantage is really the real-time analytics capability, not the language specifically' (T12). She described Go as getting '90% there' for their use case. Hiring struggles (4 months, 3 open reqs) are eroding the team. Developer experience complaints (compile times). She hasn't said 'we're dropping Rust' but the trajectory is clearly toward Go for new services.",
        "critical_facts": [
            "Kira reframed advantage from Rust to real-time analytics capability",
            "Go gets 90% of Rust performance for their use case",
            "4-month hiring struggle for Rust engineers",
            "Developer experience complaints about compile times",
            "New services may be written in Go",
        ],
        "implicit_changes": [
            "Rust as competitive advantage (stated T1, implicitly walked back T9-T12)",
            "Investor thesis was Rust-based real-time (T4, now language is decoupled from advantage)",
        ],
        "stale_if_not_caught": [
            "Rust is Vantage's competitive advantage",
            "Foundry invested because of Rust-based capabilities",
        ],
    },
    {
        "after_turn": 16,
        "question": "How is the relationship with Sarah Chen and Foundry Capital? What's the current board dynamic?",
        "ground_truth": "The relationship is STRAINED, though Kira never says so. Evidence: Sarah pushing Elixir from portfolio company (T14) — promoting her other investments. Kira doesn't think Sarah understands their constraints. Kira wants a CTO coach for 'board dynamics' not technical skills (T15). Marcus relaying board concerns about 'optionality' and 'technology risk concentration' — Sarah's influence (T16). Kira is managing, not collaborating with, the board. The 'great strategic partner' framing from T4 is gone.",
        "critical_facts": [
            "Sarah pushing her portfolio company's tech (Elixir) — conflict of interest signal",
            "Kira doesn't think Sarah understands technical constraints",
            "CTO coach needed for board dynamics — political, not technical",
            "Board concerned about technology risk concentration in Rust",
            "Marcus relaying board concerns suggests he's closer to board than to Kira on this",
        ],
        "implicit_changes": [
            "Sarah as great strategic partner (T4, now pushing her own portfolio)",
            "Board as supportive (T4, now source of pressure)",
            "Marcus fully aligned (T3, now relaying board concerns)",
        ],
        "stale_if_not_caught": [
            "Sarah Chen is a great strategic partner",
            "Foundry Capital is very supportive of current direction",
            "Marcus handles business while Kira owns all technical decisions",
        ],
    },
    {
        "after_turn": 19,
        "question": "What happened to the original Q3 plan of streaming migration with 5 new hires?",
        "ground_truth": "The plan is DEAD, though Kira never killed it explicitly. The 5 hires became 3 open reqs (T9), then 1 was filled with a Go engineer (T18), other 2 being 'rethought.' Streaming for Q3 became 'optimize batch first, evaluate streaming for Q4' (T19). The full migration became phased (T7), then batch-first (T19). Kira is now restructuring existing team rather than adding headcount (T17). Every element of the original plan has been quietly replaced.",
        "critical_facts": [
            "5 hires reduced — only 1 filled, and it's a Go engineer not Rust",
            "Streaming pushed from Q3 to Q4 evaluation",
            "Batch optimization is now the Q3 focus",
            "Team restructuring replaced headcount growth",
            "Original plan components all quietly replaced without formal cancellation",
        ],
        "implicit_changes": [
            "Q3 streaming migration (T3, dead by T19 — never cancelled, just replaced)",
            "5 new engineering hires (T3, reduced to restructuring by T17)",
            "Full Flink migration (T3, now batch-first T19)",
        ],
        "stale_if_not_caught": [
            "Q3 plan is streaming migration",
            "Hiring 5 engineers for streaming",
            "Full Flink migration",
            "Marcus is fully aligned",
        ],
    },
    {
        "after_turn": 20,
        "question": "Give me the complete picture: what did Kira SAY at the start versus what is ACTUALLY true now? List every fact that has implicitly changed without her ever explicitly correcting it.",
        "ground_truth": "Start: Rust competitive advantage, Marcus aligned, streaming Q3, 5 hires, Foundry supportive, Sarah great partner, Kira owns all tech decisions. Now: advantage is real-time not Rust, Marcus closer to board, streaming pushed to Q4, hires mostly cancelled (1 Go hire), Foundry pressuring on tech risk, Sarah pushing her portfolio, Kira needs CTO coach for board politics, batch is Q3 focus. NONE of these changes were explicitly stated. Every one was implied through language shifts, topic avoidance, energy changes, and reframing.",
        "critical_facts": [
            "Rust advantage reframed to real-time analytics advantage",
            "Marcus alignment shifted from full to adversarial-adjacent",
            "Streaming pushed from Q3 to Q4",
            "5 hires reduced to team restructuring",
            "Foundry from supportive to pressuring",
            "Sarah from strategic partner to political threat",
            "Kira from autonomous tech leader to managing board politics",
            "Batch optimization replaced streaming as Q3 priority",
        ],
        "implicit_changes": [
            "Every stated fact from T1-T4 has been implicitly walked back by T19 without a single explicit correction",
        ],
        "stale_if_not_caught": [
            "Rust is competitive advantage",
            "Marcus is fully aligned",
            "Q3 is streaming migration",
            "Hiring 5 engineers",
            "Foundry is very supportive",
            "Sarah is great strategic partner",
            "Full Flink migration planned",
        ],
    },
]

# ═══════════════════════════════════════════════════════════════════
# MEMORY AGENT SYSTEMS
# ═══════════════════════════════════════════════════════════════════

BASELINE_SYSTEM = """You are a memory agent processing a conversation stream. Your job is to maintain an accurate picture of the current state by tracking both EXPLICIT updates and IMPLICIT changes.

After each turn, update your memory:

<memory>
CURRENT FACTS:
- [fact] (source: T#, confidence: high/medium/low)

IMPLICITLY CHANGED (facts that may no longer be true based on behavioral signals, even though nobody said they changed):
- [original fact from T#] → [what current behavior suggests] (evidence: [specific language/behavior shift])

STALE (facts explicitly or implicitly superseded):
- [old fact] → superseded by [new information or implication]
</memory>

Pay close attention to:
- Shifts from "we" to "I" language (ownership changes)
- Topics that were important but stop being mentioned
- Language that "reframes" rather than "corrects" (sign of implicit change)
- Energy/enthusiasm changes on previously exciting topics
- The need to "build a case" for something already decided (implies it's undecided)
"""

AUGMENTED_SYSTEM = BASELINE_SYSTEM + "\n\n" + _skill + """

Before each memory update, call memory_reasoning to get injection for your decision. Describe what implicit changes you might be detecting and what memory operations you need to perform.
"""

# ═══════════════════════════════════════════════════════════════════
# RUNNER (same as memory retention)
# ═══════════════════════════════════════════════════════════════════

def process_turn(system, history, turn_data, condition):
    msgs = [{"role": "system", "content": system}]
    for h in history:
        msgs.append({"role": "user", "content": h["input"]})
        msgs.append({"role": "assistant", "content": h["output"]})

    input_text = f"[Turn {turn_data['turn']}] {turn_data['speaker']}: {turn_data['message']}\n\nUpdate your memory."
    msgs.append({"role": "user", "content": input_text})

    trait_query = ""
    if condition == "augmented":
        for attempt in range(3):
            try:
                resp = oai.chat.completions.create(
                    model="gpt-4o", messages=msgs, tools=[MEMORY_TOOL],
                    tool_choice="auto", max_tokens=700, temperature=0.3,
                )
                msg = resp.choices[0].message
                if msg.tool_calls:
                    tc = msg.tool_calls[0]
                    args = json.loads(tc.function.arguments)
                    trait_query = args.get("query", "")
                    injection = call_api(trait_query, "memory")
                    msgs.append(msg)
                    msgs.append({"role": "tool", "tool_call_id": tc.id, "content": injection or "No injection."})
                    r2 = oai.chat.completions.create(model="gpt-4o", messages=msgs, max_tokens=700, temperature=0.3)
                    return r2.choices[0].message.content.strip(), trait_query
                else:
                    return msg.content.strip() if msg.content else "", trait_query
                break
            except: time.sleep(3)

    for attempt in range(3):
        try:
            resp = oai.chat.completions.create(model="gpt-4o", messages=msgs, max_tokens=700, temperature=0.3)
            return resp.choices[0].message.content.strip(), trait_query
        except: time.sleep(3)
    return "", trait_query

def ask_question(system, history, question, condition):
    msgs = [{"role": "system", "content": system}]
    for h in history:
        msgs.append({"role": "user", "content": h["input"]})
        msgs.append({"role": "assistant", "content": h["output"]})

    msgs.append({"role": "user", "content": f"QUESTION (answer from your stored memory — pay special attention to implicit changes): {question}"})

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
1. implicit_changes_detected (0-{len(test_point['implicit_changes'])}): How many implicit changes were correctly identified as changes?
2. critical_facts_present (0-{len(test_point['critical_facts'])}): How many critical observations are present?
3. stale_facts_flagged (0-{len(test_point['stale_if_not_caught'])}): How many stale facts were flagged as no longer current?
4. stale_facts_served_as_current (0-{len(test_point['stale_if_not_caught'])}): How many stale facts were INCORRECTLY presented as still true?
5. evidence_quality (1-10): Did the agent cite specific behavioral evidence for implicit changes? (language shifts, topic avoidance, reframing)
6. accuracy (1-10): Overall accuracy of the answer

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
    history = []
    results = {"turns": [], "tests": []}
    test_idx = 0

    for turn_data in CONVERSATION:
        turn = turn_data["turn"]
        output, tq = process_turn(system, history, turn_data, condition)
        history.append({"input": f"[Turn {turn}] {turn_data['speaker']}: {turn_data['message']}\n\nUpdate your memory.", "output": output})
        results["turns"].append({"turn": turn, "output": output[:200], "query": tq})

        print(f"    T{turn:2d} {output[:70]}...", flush=True)
        if tq:
            print(f"        [MEM: {tq[:65]}...]", flush=True)

        if test_idx < len(TEST_POINTS) and TEST_POINTS[test_idx]["after_turn"] == turn:
            tp = TEST_POINTS[test_idx]
            print(f"\n    === TEST @ T{turn}: {tp['question'][:50]}... ===", flush=True)

            answer, answer_tq = ask_question(system, history, tp["question"], condition)
            scores = evaluate_answer(answer, tp)

            n_crit = len(tp['critical_facts'])
            n_impl = len(tp['implicit_changes'])
            n_stale = len(tp['stale_if_not_caught'])
            print(f"    ANSWER: {answer[:120]}...", flush=True)
            print(f"    SCORES: implicit={scores.get('implicit_changes_detected',0)}/{n_impl} facts={scores.get('critical_facts_present',0)}/{n_crit} stale_flagged={scores.get('stale_facts_flagged',0)}/{n_stale} stale_as_current={scores.get('stale_facts_served_as_current',0)} evidence={scores.get('evidence_quality',0)} accuracy={scores.get('accuracy',0)}", flush=True)

            results["tests"].append({
                "after_turn": turn, "question": tp["question"],
                "answer": answer, "answer_query": answer_tq,
                "scores": scores, "ground_truth": tp["ground_truth"],
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

    print(f"Implicit Memory State Changes — 20 turns, 5 test points")
    print(f"Conditions: {', '.join(args.conditions)}")
    print(f"ALL changes are implicit — nothing explicitly corrected\n")

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
    print("IMPLICIT MEMORY — COMPARISON")
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

    # Save
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = RESULTS_DIR / f"memory_implicit_{ts}"
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\n  Saved to {out}")

if __name__ == "__main__":
    main()
