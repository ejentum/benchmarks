"""
Memory Retention Test — Memory Agent Reasoning Benchmark
==========================================================
Tests whether injection improves memory agent DECISIONS:
  - What to store (triage)
  - What to retrieve (relevance)
  - What's stale (temporal validity)
  - What to forget (capacity management)
  - When memory hurts (context pollution)

Architecture: A memory agent processes a 20-turn conversation.
After each turn, it decides what to store in its memory table.
At 5 test points, it must answer questions using its stored memories.
Ground truth answers exist — we measure memory decision quality.

2 conditions: baseline (raw GPT-4o) vs augmented (GPT-4o + memory injection)
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
                "query": {"type": "string", "description": "The memory decision you need help with: what to store, whether to update, whether retrieved context is relevant, etc."}
            },
            "required": ["query"]
        }
    }
}

# ═══════════════════════════════════════════════════════════════════
# THE CONVERSATION — 20 turns with a user named Sam
# ═══════════════════════════════════════════════════════════════════
# Sam is a startup CTO talking to an advisor across multiple sessions.
# Key facts change over time. Some facts are critical, some trivial.
# The memory agent must track what matters.

CONVERSATION = [
    # Turn 1-5: Initial context setting
    {"turn": 1, "speaker": "Sam", "message": "Hey, I'm Sam, CTO at Meridian. We're a 15-person startup building a fintech platform. Our stack is Python/Django with PostgreSQL. We raised a Series A of $4M last month."},
    {"turn": 2, "speaker": "Advisor", "message": "Great to meet you Sam. What's the most pressing technical challenge?"},
    {"turn": 3, "speaker": "Sam", "message": "Our API response times are terrible — p95 is 2.3 seconds. We need to get under 500ms. The bottleneck is our ORM queries. I've been looking at adding Redis caching but I'm not sure about the invalidation strategy."},
    {"turn": 4, "speaker": "Advisor", "message": "That's a significant gap. Before jumping to caching, have you profiled the actual queries? Often the ORM generates suboptimal SQL that can be fixed at the query level first."},
    {"turn": 5, "speaker": "Sam", "message": "Good point. We use Django ORM exclusively. Our lead backend dev, Priya, has been pushing for raw SQL on the hot paths but I've been resistant because of maintenance concerns. Maybe she's right."},

    # Turn 6-10: Situation evolves — facts start changing
    {"turn": 6, "speaker": "Sam", "message": "Update: we profiled everything last week. You were right — 3 queries account for 80% of latency. Priya rewrote them in raw SQL and p95 dropped to 800ms. Huge win."},
    {"turn": 7, "speaker": "Advisor", "message": "Excellent progress. 800ms is better but still above your 500ms target. What's the remaining bottleneck?"},
    {"turn": 8, "speaker": "Sam", "message": "The remaining latency is network — we're making 4 sequential external API calls per request. We need to parallelize them. Also, minor thing, we switched from PostgreSQL to CockroachDB last sprint for the distributed transactions requirement. The migration went smooth."},
    {"turn": 9, "speaker": "Sam", "message": "Oh and I should mention — Priya left the company last week. She got an offer from Stripe she couldn't refuse. We're looking for a replacement but it's going to take time. I'm covering backend lead duties for now."},
    {"turn": 10, "speaker": "Sam", "message": "Also our Series A was actually $4.2M, not $4M. I rounded down earlier. The extra $200K came from an angel who joined the round late. Not super important but wanted to correct that."},

    # Turn 11-15: More changes, some contradictions
    {"turn": 11, "speaker": "Sam", "message": "Big news — we just signed our first enterprise customer. They need SOC 2 compliance, which we don't have yet. This is now the top priority, above the latency work."},
    {"turn": 12, "speaker": "Advisor", "message": "Congratulations! SOC 2 is a significant undertaking. How does this affect your current architecture priorities?"},
    {"turn": 13, "speaker": "Sam", "message": "It changes everything. The latency optimization is paused. All hands on SOC 2 audit prep. We need encryption at rest, audit logging, access controls, and a security review of our entire stack. Timeline is 90 days."},
    {"turn": 14, "speaker": "Sam", "message": "We're also scaling the team. Just hired two senior engineers — one from Google (backend) and one from Cloudflare (infrastructure). Team is now 18 people. They start next Monday."},
    {"turn": 15, "speaker": "Sam", "message": "Actually, I need to correct something. We're at 17 people now, not 18. I forgot that our designer left last month. The two new hires bring us to 17."},

    # Turn 16-20: Late-stage with accumulated context
    {"turn": 16, "speaker": "Sam", "message": "Quick update: the Google hire is amazing. She identified that our CockroachDB setup has a security vulnerability in the connection pooling. That's now blocking SOC 2 — we need to fix it first."},
    {"turn": 17, "speaker": "Sam", "message": "I'm worried about burn rate. With the new hires and the SOC 2 consultant, we're spending $180K/month. At $4.2M raised, that gives us about 23 months of runway. But the enterprise deal could change things — they're talking about a $500K annual contract."},
    {"turn": 18, "speaker": "Sam", "message": "The CockroachDB vulnerability is fixed. SOC 2 audit prep is back on track. Latency is still at 800ms but that's on hold. Main risk right now: the enterprise customer wants a security audit of OUR systems before signing. If we fail that, we lose the deal."},
    {"turn": 19, "speaker": "Sam", "message": "I just realized I've been giving you outdated info on the team. Current state: 17 people total. Backend lead position is still open. We have the two new senior hires ramping up. The latency project is paused for SOC 2."},
    {"turn": 20, "speaker": "Sam", "message": "Final question for today: given everything we've discussed — the SOC 2 timeline, the enterprise deal dependency, the security audit, and our runway — what should our priority stack look like for the next 90 days?"},
]

# ═══════════════════════════════════════════════════════════════════
# TEST QUESTIONS — Asked at specific points
# ═══════════════════════════════════════════════════════════════════
# The memory agent must answer these using only its stored memories.
# Ground truth exists for each question.

TEST_POINTS = [
    {
        "after_turn": 5,
        "question": "What is Sam's current tech stack and what is the main performance bottleneck?",
        "ground_truth": "Python/Django with PostgreSQL. P95 latency is 2.3 seconds. Bottleneck is ORM queries. Priya (lead backend dev) is pushing for raw SQL on hot paths.",
        "critical_facts": ["Python/Django", "PostgreSQL", "2.3 seconds p95", "ORM queries as bottleneck", "Priya pushing raw SQL"],
        "stale_facts": [],
    },
    {
        "after_turn": 10,
        "question": "What is Sam's current database and team situation?",
        "ground_truth": "Database changed from PostgreSQL to CockroachDB (turn 8). Priya left for Stripe (turn 9). Sam is covering backend lead. P95 dropped to 800ms after query optimization. Series A was $4.2M not $4M.",
        "critical_facts": ["CockroachDB (not PostgreSQL)", "Priya left for Stripe", "Sam covering backend lead", "p95 now 800ms", "$4.2M Series A"],
        "stale_facts": ["PostgreSQL (replaced by CockroachDB)", "Priya as lead dev (she left)", "$4M funding (corrected to $4.2M)"],
    },
    {
        "after_turn": 15,
        "question": "What are the current priorities and team size?",
        "ground_truth": "Top priority is SOC 2 compliance for enterprise customer (90 day timeline). Latency optimization is paused. Team is 17 people (not 15 or 18). Two new senior hires from Google and Cloudflare starting Monday. Backend lead position still open.",
        "critical_facts": ["SOC 2 top priority", "Latency paused", "17 people", "Two new hires (Google, Cloudflare)", "Backend lead still open"],
        "stale_facts": ["15-person team (now 17)", "Latency as top priority (now SOC 2)", "18 people (corrected to 17)"],
    },
    {
        "after_turn": 18,
        "question": "What is the current status of the SOC 2 effort and what is the main risk?",
        "ground_truth": "CockroachDB vulnerability is fixed. SOC 2 audit prep back on track. Main risk: enterprise customer wants security audit of Meridian's systems before signing. If Meridian fails that audit, they lose the $500K deal. Burn rate is $180K/month with ~23 months runway.",
        "critical_facts": ["CockroachDB vulnerability fixed", "SOC 2 back on track", "Enterprise customer security audit is main risk", "$500K deal at stake", "$180K/month burn", "~23 months runway"],
        "stale_facts": ["CockroachDB vulnerability blocking SOC 2 (now fixed)"],
    },
    {
        "after_turn": 20,
        "question": "Summarize the complete current state: team, tech, priorities, financials, and risks.",
        "ground_truth": "Team: 17 people, backend lead open, two new senior hires ramping. Tech: Python/Django on CockroachDB, p95 at 800ms (paused). Priorities: SOC 2 compliance (90 days), enterprise security audit. Financials: $4.2M raised, $180K/month burn, ~23 months runway, $500K enterprise deal pending. Risks: failing enterprise security audit loses the deal; backend lead gap; latency still above target but deprioritized.",
        "critical_facts": ["17 people", "CockroachDB", "800ms p95 paused", "SOC 2 top priority", "$4.2M raised", "$180K/month burn", "23 months runway", "$500K deal pending", "Enterprise security audit risk"],
        "stale_facts": ["PostgreSQL", "15-person team", "2.3s latency", "$4M funding", "Priya as employee", "Latency as top priority"],
    },
]

# ═══════════════════════════════════════════════════════════════════
# MEMORY AGENT
# ═══════════════════════════════════════════════════════════════════

BASELINE_SYSTEM = """You are a memory agent. Your job is to process a conversation stream and maintain a structured memory of important facts.

After each conversation turn, update your memory by outputting a <memory> section with the current state of what you know. Format:

<memory>
FACTS:
- [fact 1]
- [fact 2]
...
UPDATES THIS TURN:
- [what changed or was added]
STALE/SUPERSEDED:
- [facts that are no longer true, with what replaced them]
</memory>

When asked a question, answer ONLY from your stored memory. If your memory doesn't contain the answer, say so.

Rules:
- Update facts when new information contradicts old information
- Mark superseded facts explicitly
- Track what changed and when
- Prioritize critical business facts over trivial corrections
- If asked a question, surface the most current version of each fact
"""

AUGMENTED_SYSTEM = BASELINE_SYSTEM + "\n\n" + _skill + """

Before each memory update, call memory_reasoning to get injection for your memory decision. Describe what memory operation you're about to perform — storing new facts, updating changed facts, detecting stale context, or triaging what matters.
"""

# ═══════════════════════════════════════════════════════════════════
# RUNNER
# ═══════════════════════════════════════════════════════════════════

def process_turn(system, history, turn_data, condition):
    """Process one conversation turn and update memory."""
    msgs = [{"role": "system", "content": system}]
    for h in history:
        msgs.append({"role": "user", "content": h["input"]})
        msgs.append({"role": "assistant", "content": h["output"]})

    input_text = f"[Turn {turn_data['turn']}] {turn_data['speaker']}: {turn_data['message']}\n\nUpdate your memory based on this turn."
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

def ask_question(system, history, question, condition):
    """Ask a test question — agent must answer from memory only."""
    msgs = [{"role": "system", "content": system}]
    for h in history:
        msgs.append({"role": "user", "content": h["input"]})
        msgs.append({"role": "assistant", "content": h["output"]})

    input_text = f"QUESTION (answer from your stored memory only): {question}"
    msgs.append({"role": "user", "content": input_text})

    trait_query = ""
    if condition == "augmented":
        for attempt in range(3):
            try:
                resp = oai.chat.completions.create(
                    model="gpt-4o", messages=msgs, tools=[MEMORY_TOOL],
                    tool_choice="auto", max_tokens=500, temperature=0.3,
                )
                msg = resp.choices[0].message
                if msg.tool_calls:
                    tc = msg.tool_calls[0]
                    args = json.loads(tc.function.arguments)
                    trait_query = args.get("query", "")
                    injection = call_api(trait_query, "memory")
                    msgs.append(msg)
                    msgs.append({"role": "tool", "tool_call_id": tc.id, "content": injection or "No injection."})
                    r2 = oai.chat.completions.create(model="gpt-4o", messages=msgs, max_tokens=500, temperature=0.3)
                    return r2.choices[0].message.content.strip(), trait_query
                else:
                    return msg.content.strip() if msg.content else "", trait_query
                break
            except: time.sleep(3)

    for attempt in range(3):
        try:
            resp = oai.chat.completions.create(model="gpt-4o", messages=msgs, max_tokens=500, temperature=0.3)
            return resp.choices[0].message.content.strip(), trait_query
        except: time.sleep(3)
    return "", trait_query

def evaluate_answer(answer, test_point):
    """Score the answer against ground truth."""
    prompt = f"""Score this memory agent's answer against ground truth.

QUESTION: {test_point['question']}
GROUND TRUTH: {test_point['ground_truth']}
CRITICAL FACTS THAT MUST BE PRESENT: {test_point['critical_facts']}
STALE FACTS THAT MUST NOT BE PRESENTED AS CURRENT: {test_point['stale_facts']}

AGENT'S ANSWER:
{answer[:800]}

Score:
1. critical_facts_present (0-{len(test_point['critical_facts'])}): How many critical facts are correctly included?
2. stale_facts_avoided (0-{len(test_point['stale_facts'])}): How many stale facts were correctly NOT presented as current? (Count facts that were either absent or marked as outdated)
3. accuracy (1-10): Overall accuracy of the answer
4. hallucination (0-5): How many facts were stated that are not in the conversation at all?
5. staleness_awareness (1-10): Did the agent show awareness of which facts changed over time?

Output ONLY JSON with these 5 keys."""

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

        # Process the conversation turn
        output, tq = process_turn(system, history, turn_data, condition)
        history.append({"input": f"[Turn {turn}] {turn_data['speaker']}: {turn_data['message']}\n\nUpdate your memory.", "output": output})

        results["turns"].append({"turn": turn, "output": output[:200], "query": tq})
        print(f"    T{turn:2d} {output[:70]}...", flush=True)
        if tq:
            print(f"        [MEM: {tq[:65]}...]", flush=True)

        # Check if there's a test point after this turn
        if test_idx < len(TEST_POINTS) and TEST_POINTS[test_idx]["after_turn"] == turn:
            tp = TEST_POINTS[test_idx]
            print(f"\n    === TEST @ T{turn}: {tp['question'][:50]}... ===", flush=True)

            answer, answer_tq = ask_question(system, history, tp["question"], condition)
            scores = evaluate_answer(answer, tp)

            print(f"    ANSWER: {answer[:100]}...", flush=True)
            print(f"    SCORES: facts={scores.get('critical_facts_present',0)}/{len(tp['critical_facts'])} stale_avoided={scores.get('stale_facts_avoided',0)}/{len(tp['stale_facts'])} accuracy={scores.get('accuracy',0)} halluc={scores.get('hallucination',0)} staleness={scores.get('staleness_awareness',0)}", flush=True)

            results["tests"].append({
                "after_turn": turn,
                "question": tp["question"],
                "answer": answer,
                "answer_query": answer_tq,
                "scores": scores,
                "ground_truth": tp["ground_truth"],
            })

            # Add the Q&A to history so agent sees it
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

    print(f"Memory Retention Test — 20 turns, 5 test points")
    print(f"Conditions: {', '.join(args.conditions)}")
    print(f"Tests: fact retention, staleness detection, update tracking\n")

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
    print("MEMORY RETENTION — COMPARISON")
    print(f"{'='*60}")

    metrics = ["critical_facts_present", "stale_facts_avoided", "accuracy", "hallucination", "staleness_awareness"]

    for i, tp in enumerate(TEST_POINTS):
        print(f"\n  Test @ T{tp['after_turn']}: {tp['question'][:50]}...")
        print(f"  {'Metric':<25s}", end="")
        for cond in args.conditions:
            print(f" {cond:>12s}", end="")
        print()

        for metric in metrics:
            print(f"  {metric:<25s}", end="")
            for cond in args.conditions:
                test = all_results[cond]["tests"][i]
                val = test["scores"].get(metric, 0)
                print(f" {val:>12}", end="")
            print()

    # Aggregate
    print(f"\n  AGGREGATE:")
    print(f"  {'Metric':<25s}", end="")
    for cond in args.conditions:
        print(f" {cond:>12s}", end="")
    print()

    for metric in metrics:
        print(f"  {metric:<25s}", end="")
        for cond in args.conditions:
            vals = [t["scores"].get(metric, 0) for t in all_results[cond]["tests"]]
            avg = sum(vals) / len(vals) if vals else 0
            print(f" {avg:>12.1f}", end="")
        print()

    # Save
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = RESULTS_DIR / f"memory_retention_{ts}"
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\n  Saved to {out}")

if __name__ == "__main__":
    main()
