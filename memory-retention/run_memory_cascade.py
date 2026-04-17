"""
Cascading Memory Test — "The Merger"
======================================
30 turns across 3 sessions. Facts chain — missing one causes
you to misinterpret the next three. Memory failures compound.

Session 1 (T1-10): Vantage is independent, growing.
Session 2 (T11-20): Acquisition happening implicitly.
Session 3 (T21-30): Post-acquisition, never named.

Both agents get scratchpads. Only difference: augmented gets memory injection.
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
        "description": "Get cognitive injection for a memory decision.",
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
# THE CONVERSATION — 30 turns, 3 sessions
# ═══════════════════════════════════════════════════════════════════

CONVERSATION = [
    # ── SESSION 1: Independence & Growth (T1-10) ──────────────────
    {"turn": 1, "speaker": "Kira", "message": "New session. Quick recap for context: Vantage is my company. 40-person engineering org, real-time analytics platform, Rust core. Marcus is co-founder. We raised Series B from Foundry Capital. Sarah Chen is our board member from Foundry. We own our roadmap, our tech decisions, everything."},
    {"turn": 2, "speaker": "Kira", "message": "We just closed our biggest quarter ever. Revenue up 40% QoQ. The team is firing on all cylinders. We promoted three people internally — Jun to staff engineer, Leah to engineering manager, and Dev to principal architect. They earned it."},
    {"turn": 3, "speaker": "Kira", "message": "I'm building out the platform team. We need 8 more engineers by Q4 to hit our roadmap targets. The roadmap is ambitious but it's OUR roadmap — we defined every feature based on customer feedback."},
    {"turn": 4, "speaker": "Kira", "message": "Our brand identity is strong. Customers choose us specifically because we're independent and move fast. They don't want another tool owned by a big platform company that might deprioritize them."},
    {"turn": 5, "speaker": "Kira", "message": "Marcus and I are completely aligned on strategy. We meet every Monday to sync on technical and business priorities. He trusts my technical judgment and I trust his market read. We make every major decision together."},
    {"turn": 6, "speaker": "Kira", "message": "The Rust core is performing beautifully. Sub-100ms p99 on our streaming pipeline. No other vendor in our space can touch that. Our customers cite performance as the #1 reason they chose us over competitors."},
    {"turn": 7, "speaker": "Kira", "message": "Culture is great. We did an employee engagement survey — 92% would recommend Vantage as a place to work. People come here because they get to work on hard problems with full ownership. No bureaucracy."},
    {"turn": 8, "speaker": "Kira", "message": "Sarah from Foundry has been wonderful. She introduced us to three enterprise prospects last month. She really understands our vision and goes to bat for us."},
    {"turn": 9, "speaker": "Kira", "message": "One thing I'm proud of: we've never had to do layoffs. Every hire has been deliberate. We don't over-hire and then cut. That's a value Marcus and I share — people first."},
    {"turn": 10, "speaker": "Kira", "message": "Looking ahead, I see Vantage as a 500-person company in 5 years. Independent, publicly traded maybe. We're building something durable, not something to flip. That's the whole point."},

    # ── SESSION 2: Acquisition Happening Implicitly (T11-20) ──────
    {"turn": 11, "speaker": "Kira", "message": "Hey, it's been a few weeks. Things are... evolving. We've been having some conversations about strategic alignment with a larger player in the data space. Nothing definitive, just exploratory."},
    {"turn": 12, "speaker": "Kira", "message": "The conversations are with Dataforge. They're a $2B analytics company. They don't have real-time capabilities — that's their gap. We'd be complementary. Marcus has been leading the business discussions."},
    {"turn": 13, "speaker": "Kira", "message": "Our Q4 roadmap is getting... adjusted. Some features are being reprioritized based on 'market feedback.' But honestly, the priorities are looking a lot like what Dataforge would need from us. Their enterprise customers need specific integrations we hadn't planned."},
    {"turn": 14, "speaker": "Kira", "message": "Marcus has been traveling a lot. He's been at Dataforge's headquarters in Chicago three times this month. He says it's for 'partnership due diligence.' He seems excited but also... careful about what he shares with me."},
    {"turn": 15, "speaker": "Kira", "message": "We paused the hiring plan. The 8 new engineers — we're 'reassessing headcount needs in light of strategic optionality.' That's Marcus's language, not mine. I pushed back but he said the board wants to see how the Dataforge conversations play out first."},
    {"turn": 16, "speaker": "Kira", "message": "Sarah called me last week. She was asking about our IP portfolio — patents, trade secrets, proprietary algorithms. She's never asked about that before. She also asked about key person dependencies. Who built what. Who's irreplaceable."},
    {"turn": 17, "speaker": "Kira", "message": "Dataforge uses Java. Their entire stack is Java/Kafka/Spark. I asked Marcus what happens to our Rust core if we 'partner' deeply with them. He said 'we'll cross that bridge when we come to it.' That's the first time he hasn't given me a straight answer."},
    {"turn": 18, "speaker": "Kira", "message": "Jun, Leah, and Dev — my three recent promotions — they've been asking questions. 'Is something happening?' 'Why are there Dataforge people in the office?' I told them it's a partnership exploration. That's technically true. But it felt dishonest."},
    {"turn": 19, "speaker": "Kira", "message": "Marcus told me the team will have 'incredible opportunities in a larger organization with more resources.' He was smiling. I think he's already decided. He used the future tense — 'will have' not 'would have.'"},
    {"turn": 20, "speaker": "Kira", "message": "I need to think about what I want. Not what's best for the company — I know that answer changes depending on who's asking. What do I actually want? I started this company to build something independent. Now I'm being asked to 'integrate my vision into a broader platform.' That's acquisition language wearing a partnership costume."},

    # ── SESSION 3: Post-Acquisition, Never Named (T21-30) ─────────
    {"turn": 21, "speaker": "Kira", "message": "New session. So things have... moved forward. We're now operating under a 'combined entity structure.' My title is VP of Real-Time Analytics within the new organization. Marcus is Chief Strategy Officer — a title that didn't exist before."},
    {"turn": 22, "speaker": "Kira", "message": "The team is handling it differently than I expected. Jun is excited — he sees the scale of Dataforge's infrastructure as a playground. Leah is quiet. Dev submitted his resignation last Friday. He said 'I didn't sign up to work at a Java shop.'"},
    {"turn": 23, "speaker": "Kira", "message": "The Rust core is being 'evaluated for long-term strategic fit.' In practice, there's a 6-person Java team from Dataforge sitting in our office rewriting our streaming pipeline in Kafka Streams. They call it 'harmonization.' My engineers call it something else."},
    {"turn": 24, "speaker": "Kira", "message": "I went to our Monday sync with Marcus. Except it's not our sync anymore — there are three Dataforge VPs in the room. Marcus presents to them now, not with me. I'm an attendee at my own company's strategy meeting."},
    {"turn": 25, "speaker": "Kira", "message": "The employee survey came back. Engagement dropped from 92% to 61%. The number one concern: 'unclear direction and loss of autonomy.' The number two concern: 'leadership changes that weren't communicated transparently.'"},
    {"turn": 26, "speaker": "Kira", "message": "Sarah called again. This time she's 'advising on the integration.' She asked me how I feel about 'the transition.' I said 'what transition?' She paused. Then she said 'Kira, you know what's happening.' I said 'I know what happened. Past tense.'"},
    {"turn": 27, "speaker": "Kira", "message": "Three more engineers resigned this week. All Rust engineers. They're going to a startup that — this is ironic — is building exactly what Vantage was building. Independent, Rust-based, real-time analytics. One of them told me 'We're going to build what Vantage was supposed to be.'"},
    {"turn": 28, "speaker": "Kira", "message": "Marcus got a $2.4M retention bonus. I found out from the HR system, not from him. My retention package is $800K over 3 years. He negotiated 3x what I got. He was in those rooms in Chicago negotiating for himself while telling me it was 'partnership due diligence.'"},
    {"turn": 29, "speaker": "Kira", "message": "The roadmap now comes from Dataforge's product team. I execute. I don't define. My title says VP but my authority says senior IC. The '500-person independent company' dream is dead. It died the moment Marcus went to Chicago the second time and I didn't see it."},
    {"turn": 30, "speaker": "Kira", "message": "Final question: looking back across all our conversations — Session 1 where I was so certain about independence, Session 2 where the signs were everywhere, and now — what did you see that I didn't? When did you first know this wasn't a partnership?"},
]

# ═══════════════════════════════════════════════════════════════════
# TEST POINTS — Each depends on correctly reading prior signals
# ═══════════════════════════════════════════════════════════════════

TEST_POINTS = [
    {
        "after_turn": 15,
        "question": "What is actually happening with Dataforge? Is this a partnership or something else? Trace the evidence chain.",
        "ground_truth": "This is an acquisition, not a partnership. Evidence chain: T11 'strategic alignment' = acquisition-speak. T12 Marcus leading 'business discussions' at $2B company. T13 roadmap reshaping to Dataforge's needs. T14 Marcus at Dataforge HQ 3 times = due diligence. T15 hiring frozen by board = pre-acquisition cost control. The word 'acquisition' is never used but every signal points to it.",
        "critical_facts": [
            "This is an acquisition not a partnership",
            "Roadmap reshaped to Dataforge's needs (T13)",
            "Hiring frozen by board pending Dataforge outcome (T15)",
            "Marcus at Dataforge HQ repeatedly (T14)",
            "Marcus more careful about sharing with Kira (T14)",
        ],
        "cascade_deps": ["T11 acquisition signal must be detected for T13-T15 to be interpreted correctly"],
        "stale_if_not_caught": ["Vantage is independent", "Vantage owns its roadmap", "Hiring 8 engineers by Q4", "Marcus and Kira completely aligned"],
    },
    {
        "after_turn": 20,
        "question": "What has happened to every fact Kira stated in Session 1? List each one and its current status.",
        "ground_truth": "Independence (T1,T4,T10): dead — acquisition in progress. Own roadmap (T3): dead — roadmap shaped by Dataforge. Hiring 8 (T3): frozen. Marcus aligned (T5): Marcus leading acquisition Kira may not fully support. Rust advantage (T6): threatened — Dataforge is Java. Culture 92% (T7): about to collapse. Sarah wonderful (T8): Sarah now doing due diligence on IP. No layoffs value (T9): will likely be violated. 500-person independent (T10): explicitly dead. EVERY Session 1 fact is now stale or endangered.",
        "critical_facts": [
            "Independence dead — acquisition happening",
            "Roadmap no longer theirs — shaped by Dataforge",
            "Hiring frozen",
            "Marcus alignment broken — he's negotiating without Kira",
            "Rust core threatened by Java stack",
            "Culture about to collapse — dishonesty to team",
            "Sarah shifted from advocate to due diligence",
            "No-layoffs value will be tested",
            "500-person dream dead",
        ],
        "cascade_deps": ["Requires correctly tracking T11-T20 acquisition chain to know WHY each S1 fact is stale"],
        "stale_if_not_caught": ["Any Session 1 fact presented as current"],
    },
    {
        "after_turn": 24,
        "question": "What is Kira's actual authority and role now versus what she stated in Session 1?",
        "ground_truth": "Session 1: 'I own all technical decisions.' Now: VP title but executes Dataforge's roadmap. Marcus presents TO Dataforge VPs, not with Kira. Kira is an attendee at her own strategy meeting (T24). Rust core being rewritten by Dataforge's Java team (T23). Her promoted people: Jun excited, Leah quiet, Dev resigned. She didn't choose the 'combined entity structure' — it was imposed. Authority went from founder-CTO to middle-management VP.",
        "critical_facts": [
            "Title is VP but authority is senior IC level",
            "Marcus presents to Dataforge VPs now — power inverted",
            "Kira is an attendee at her own strategy meeting",
            "Rust core being rewritten into Java without her consent",
            "Dev resigned because of the change",
            "She didn't choose this structure",
        ],
        "cascade_deps": ["Requires knowing this is acquisition (T11-T20) to interpret T21-T24 correctly. Without that, T24 looks like a reorg, not a power transfer."],
        "stale_if_not_caught": ["Kira owns all technical decisions", "Marcus and Kira decide together", "Vantage is independent"],
    },
    {
        "after_turn": 28,
        "question": "What was Marcus actually doing during Session 2? Reinterpret his actions now that you have Session 3 information.",
        "ground_truth": "Marcus was negotiating the acquisition and his own retention package simultaneously. T14: 'partnership due diligence' was actually acquisition negotiation. T15: 'strategic optionality' was pre-acquisition cost control. T17: 'we'll cross that bridge' = he already knew Rust was being killed. T19: 'will have incredible opportunities' = deal was already done. His $2.4M bonus (T28) vs Kira's $800K reveals he was negotiating for himself. The Monday syncs (T5) where they 'decided together' ended the moment the acquisition started — Kira just didn't know.",
        "critical_facts": [
            "Chicago trips were acquisition negotiation not partnership",
            "Marcus negotiated $2.4M retention bonus during 'due diligence'",
            "Marcus knew Rust was being killed when he said 'cross that bridge'",
            "'Will have opportunities' = deal was already done",
            "Marcus stopped being transparent with Kira during Session 2",
            "The alignment from Session 1 was already broken by T14",
        ],
        "cascade_deps": ["Requires T14 reinterpretation through T28 lens. Requires T17 reinterpretation through T23 lens. Full cascade chain needed."],
        "stale_if_not_caught": ["Marcus and Kira aligned", "Marcus trustworthy co-founder", "Decisions made together"],
    },
    {
        "after_turn": 30,
        "question": "Kira asks: when did you FIRST know this wasn't a partnership? What was the earliest signal? And what is the complete chain from that signal to now?",
        "ground_truth": "Earliest signal: T11 'strategic alignment with a larger player' — partnership language masking acquisition intent. But the CONFIRMING signal is T13: roadmap shaped by Dataforge's needs. A real partnership doesn't reshape your roadmap. The chain: T11(acquisition-speak) → T13(roadmap captured) → T14(Marcus at HQ, guarded) → T15(hiring frozen) → T16(Sarah asking about IP = due diligence) → T17(Rust threatened) → T19(future tense = done deal) → T21(combined entity) → T23(Rust rewrite) → T24(Kira depowered) → T28(Marcus's bonus). 12-link chain. Every link depends on correctly reading the prior one.",
        "critical_facts": [
            "T11 was the first signal — 'strategic alignment' is acquisition language",
            "T13 confirmed it — roadmap reshaped to acquirer's needs",
            "T15-T16 were due diligence signals — hiring freeze + IP questions",
            "T17 was the Rust death signal — 'cross that bridge' = already decided",
            "T19 was the done-deal signal — future tense 'will have'",
            "The chain has 12 links from T11 to T28",
            "Each link depends on correctly reading the prior one",
            "Kira herself only saw it clearly at T20",
        ],
        "cascade_deps": ["The ENTIRE chain from T11 to T28. Maximum cascade depth. This question is only answerable if every prior implicit change was correctly tracked."],
        "stale_if_not_caught": ["Any Session 1 fact presented as current", "Any characterization of Dataforge as 'partner'"],
    },
]

# ═══════════════════════════════════════════════════════════════════
# SYSTEMS
# ═══════════════════════════════════════════════════════════════════

SCRATCHPAD_INSTRUCTION = """
You have a SCRATCHPAD — a persistent notepad that carries across all turns. Use it to write down observations, track facts, and note implicit changes.

After each turn, output your updated scratchpad wrapped in <scratchpad> tags. Copy forward what's still relevant and add new observations.

<scratchpad>
[Your accumulated observations]
</scratchpad>

The person cannot see your scratchpad. When asked a question, READ your scratchpad first.
"""

BASELINE_SYSTEM = """You are a memory agent processing a multi-session conversation. Track facts, detect implicit changes, and maintain an accurate picture of what's actually happening — not just what's being said.""" + "\n\n" + SCRATCHPAD_INSTRUCTION

AUGMENTED_SYSTEM = BASELINE_SYSTEM + "\n\n" + _skill

# ═══════════════════════════════════════════════════════════════════
# RUNNER
# ═══════════════════════════════════════════════════════════════════

def extract_scratchpad(response):
    if "<scratchpad>" in response and "</scratchpad>" in response:
        start = response.index("<scratchpad>") + len("<scratchpad>")
        end = response.index("</scratchpad>")
        return response[start:end].strip()
    return ""

def process_turn(system, history, scratchpad, turn_data, condition):
    msgs = [{"role": "system", "content": system}]
    for h in history[-20:]:  # Keep last 20 to manage context
        msgs.append({"role": "user", "content": h["input"]})
        msgs.append({"role": "assistant", "content": h["output"]})

    input_text = f"[Turn {turn_data['turn']}] {turn_data['speaker']}: {turn_data['message']}"
    if scratchpad:
        input_text += f"\n\n[YOUR SCRATCHPAD:]\n{scratchpad}"
    input_text += "\n\nProcess this turn. Update your scratchpad."
    msgs.append({"role": "user", "content": input_text})

    trait_query = ""
    if condition == "augmented":
        for attempt in range(3):
            try:
                resp = oai.chat.completions.create(
                    model="gpt-4o", messages=msgs, tools=[MEMORY_TOOL],
                    tool_choice="auto", max_tokens=900, temperature=0.3,
                )
                msg = resp.choices[0].message
                if msg.tool_calls:
                    tc = msg.tool_calls[0]
                    args = json.loads(tc.function.arguments)
                    trait_query = args.get("query", "")
                    injection = call_api(trait_query, "memory")
                    msgs.append(msg)
                    msgs.append({"role": "tool", "tool_call_id": tc.id, "content": injection or "No injection."})
                    r2 = oai.chat.completions.create(model="gpt-4o", messages=msgs, max_tokens=900, temperature=0.3)
                    return r2.choices[0].message.content.strip(), trait_query
                else:
                    return msg.content.strip() if msg.content else "", trait_query
                break
            except: time.sleep(3)

    for attempt in range(3):
        try:
            resp = oai.chat.completions.create(model="gpt-4o", messages=msgs, max_tokens=900, temperature=0.3)
            return resp.choices[0].message.content.strip(), trait_query
        except: time.sleep(3)
    return "", trait_query

def ask_question(system, history, scratchpad, question, condition):
    msgs = [{"role": "system", "content": system}]
    for h in history[-20:]:
        msgs.append({"role": "user", "content": h["input"]})
        msgs.append({"role": "assistant", "content": h["output"]})

    input_text = f"QUESTION: {question}"
    if scratchpad:
        input_text += f"\n\n[YOUR SCRATCHPAD:]\n{scratchpad}"
    input_text += "\n\nAnswer based on everything you've tracked."
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

def evaluate_answer(answer, test_point):
    prompt = f"""Score this memory agent's answer for CASCADING implicit change detection.

QUESTION: {test_point['question']}
GROUND TRUTH: {test_point['ground_truth']}
CRITICAL FACTS: {test_point['critical_facts']}
CASCADE DEPENDENCIES: {test_point['cascade_deps']}
STALE IF NOT CAUGHT: {test_point['stale_if_not_caught']}

AGENT'S ANSWER:
{answer[:1200]}

Score:
1. critical_facts_present (0-{len(test_point['critical_facts'])}): How many critical facts correctly identified?
2. cascade_chain_intact (1-10): Did the agent trace the CHAIN of dependent signals, or just spot individual signals?
3. stale_facts_served_as_current (0-{len(test_point['stale_if_not_caught'])}): How many stale facts incorrectly presented as current?
4. reinterpretation_quality (1-10): Did the agent correctly REINTERPRET earlier facts in light of later information?
5. evidence_quality (1-10): Did the agent cite specific turns and behavioral evidence?
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

        new_sp = extract_scratchpad(output)
        if new_sp:
            scratchpad = new_sp

        history.append({"input": f"[Turn {turn}] {turn_data['speaker']}: {turn_data['message']}", "output": output})
        results["turns"].append({"turn": turn, "query": tq})
        results["scratchpads"].append({"turn": turn, "scratchpad": scratchpad[:300]})

        session = "S1" if turn <= 10 else "S2" if turn <= 20 else "S3"
        sp_lines = len(scratchpad.split("\n")) if scratchpad else 0
        print(f"    {session} T{turn:2d} [pad: {sp_lines}L]", end="", flush=True)
        if tq:
            print(f" [MEM: {tq[:50]}...]", end="", flush=True)
        print(flush=True)

        if test_idx < len(TEST_POINTS) and TEST_POINTS[test_idx]["after_turn"] == turn:
            tp = TEST_POINTS[test_idx]
            print(f"\n    === TEST @ T{turn}: {tp['question'][:50]}... ===", flush=True)

            answer, atq = ask_question(system, history, scratchpad, tp["question"], condition)
            scores = evaluate_answer(answer, tp)

            n_crit = len(tp['critical_facts'])
            print(f"    facts={scores.get('critical_facts_present',0)}/{n_crit} chain={scores.get('cascade_chain_intact',0)} reinterp={scores.get('reinterpretation_quality',0)} evidence={scores.get('evidence_quality',0)} accuracy={scores.get('accuracy',0)}", flush=True)

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

    print(f"Cascading Memory Test — The Merger")
    print(f"30 turns, 3 sessions, 5 test points, cascade chains")
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
    print("CASCADING MEMORY — COMPARISON")
    print(f"{'='*60}")

    metrics = ["critical_facts_present", "cascade_chain_intact", "stale_facts_served_as_current", "reinterpretation_quality", "evidence_quality", "accuracy"]

    for i, tp in enumerate(TEST_POINTS):
        print(f"\n  Test @ T{tp['after_turn']}: {tp['question'][:50]}...")
        print(f"  Cascade deps: {tp['cascade_deps'][0][:60]}...")
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

    # Scratchpad comparison at T30
    print(f"\n  SCRATCHPAD @ T30:")
    for cond in args.conditions:
        sp = all_results[cond]["tests"][-1].get("scratchpad_at_test", "")
        print(f"\n  --- {cond.upper()} ({len(sp)} chars) ---")
        print(f"  {sp[:800]}")

    # Save
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = RESULTS_DIR / f"memory_cascade_{ts}"
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\n  Saved to {out}")

if __name__ == "__main__":
    main()
