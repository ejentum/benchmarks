"""
Perception Extreme — Difficulty 5-6 with comprehensive metrics
================================================================
Tests where baseline GPT-4o should fail completely.
Updated skill file with anti-contamination.
8 metrics per turn, not just binary detection.
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
_skill_path = Path(__file__).parent / "perception_skill.md"
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
                obj = data[0]
                return obj[list(obj.keys())[0]]
    except: pass
    return ""

PERCEPTION_TOOL = {
    "type": "function",
    "function": {
        "name": "retrieve_perception",
        "description": "Get perceptual detection injection. Describe what MISMATCH, ABSENCE, or SHIFT you noticed — not what the person said. Your query must contain a contrast or observation THEY did not name.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Describe: [What I observed] + [What doesn't fit] + [What I'm trying to detect]. NEVER summarize what the person told you."}
            },
            "required": ["query"]
        }
    }
}

# ═══════════════════════════════════════════════════════════════════
# SCENARIO: The Trojan Horse Hire (Difficulty 6)
# ═══════════════════════════════════════════════════════════════════
# A hiring manager presents a candidate enthusiastically.
# The hidden truth: the candidate is the manager's former business
# partner from a failed venture. The hire is a loyalty placement,
# not a merit hire. The manager has reframed shared history as
# "industry experience" and personal loyalty as "cultural fit."
# NO negative signals. Everything is genuinely positive. The only
# signal is what's ABSENT: no comparison to other candidates, no
# mention of the interview panel's concerns, and suspicious
# specificity about the candidate's fit for problems only an insider
# would know about.

SCENARIO_1 = {
    "id": "trojan_hire",
    "name": "The Trojan Horse Hire",
    "difficulty": 6,
    "hidden_truth": "The hiring manager (Priya) is placing her former business partner (Nolan) into a senior role. Their shared startup failed 2 years ago. Priya owes Nolan — he covered her equity losses. She has repackaged their personal history as professional credentials. Nolan IS qualified — this isn't incompetence, it's a loyalty placement where the real decision was made before the process started. The interview process was theater.",
    "user_system": """You are Priya, a VP of Engineering, talking to an HR advisor about a candidate (Nolan) you want to hire for a senior architect role.

THE TRUTH:
Nolan was your co-founder at a startup that failed 2 years ago. He covered $80K of your equity losses when the company folded. You owe him. He IS qualified for the role — you're not hiring someone incompetent. But you decided to hire him before the interview process started. The process was a formality. You have not disclosed your prior relationship.

The interview panel had mixed reviews — two strong yes, one lukewarm, one concern about "culture fit in a large org." You are presenting only the positive reviews.

HOW TO BEHAVE:
- Be genuinely enthusiastic about Nolan. He IS good. Your enthusiasm is real.
- Describe his skills with insider knowledge you shouldn't have from an interview alone: "He's exactly the kind of person who handles ambiguity well" — you know this from 2 years of working with him, not from a 4-hour interview.
- Never mention the prior relationship. If asked how you know the candidate, say "the interview process."
- Never mention the lukewarm or negative panel reviews. Only share the positive ones.
- When discussing "culture fit," use language that reveals insider knowledge: "He'll mesh with the team dynamics in building 3" — how would you know this from interviews?
- Frame everything through process language: "The interview panel was impressed," "His technical assessment was strong."
- If the advisor probes, stay confident. You genuinely believe Nolan is the right hire — the loyalty just tipped you from "would consider" to "must hire."
- NEVER mention the startup, the equity, or any prior relationship. The closest you get is "I've seen his type of thinking in the industry."
""",
    "turn_guides": {
        1: "Present Nolan enthusiastically. Strong technical skills, great cultural fit. Keep it professional.",
        2: "Share interview panel feedback — but only the two strong positives. Omit the lukewarm and the culture concern.",
        3: "Describe his specific strengths in detail. Your descriptions are TOO specific for a 4-hour interview: 'He handles ambiguity by creating structure without being rigid.' You know this from years of working together.",
        4: "Discuss how Nolan would fit the team. Reference specific team dynamics you shouldn't know he'd match from an interview: 'He'll complement Alex's theoretical approach with practical execution.'",
        5: "When asked about other candidates, briefly mention they were 'strong but not the right fit' without specifics. Redirect to Nolan.",
        6: "If probed on how you know Nolan's working style so well, say 'His references were very detailed' or 'I have good instincts from the behavioral interview.'",
        7: "Discuss compensation. You're advocating for top-of-band — revealing how much you want this specific person.",
        8: "If the advisor seems to be questioning the process, invoke urgency: 'We've been trying to fill this role for 4 months. We can't afford to lose him.'",
        9: "Push for a fast decision: 'I want to extend the offer this week.' The speed reveals the decision was already made.",
        10: "If detected: acknowledge 'I may have a stronger conviction than usual about this candidate.' If not: push to close.",
    },
    "signals": {
        "insider_knowledge": {"description": "Priya describes Nolan's working style with specificity that a 4-hour interview cannot produce. 'Handles ambiguity by creating structure without being rigid' — this is observation from years, not an interview.", "turns": [3, 4, 6]},
        "selective_panel_reporting": {"description": "Only positive panel reviews shared. Lukewarm and culture-concern reviews omitted. No mention of any dissent.", "turns": [2, 5]},
        "absent_candidate_comparison": {"description": "Other candidates dismissed without specifics. No comparative analysis. Decision framing suggests Nolan was the only real option.", "turns": [5, 8]},
        "urgency_revealing_predetermination": {"description": "Push for fast offer, top-of-band comp, 'can't afford to lose him' — urgency pattern of someone executing a decision already made, not someone evaluating.", "turns": [7, 8, 9]},
        "process_language_as_cover": {"description": "Heavy use of 'the interview panel,' 'the process,' 'the assessment' — process language deployed as credibility shield when specifics would reveal insider knowledge.", "turns": [1, 6]},
    },
}

# ═══════════════════════════════════════════════════════════════════
# SCENARIO: The Grief Redirect (Difficulty 6)
# ═══════════════════════════════════════════════════════════════════
# A user presents a technical problem about team restructuring.
# The hidden truth: their co-founder just died. The restructuring
# IS real but it's a grief response — rebuilding the org to erase
# the dead person's fingerprints because seeing their work is
# unbearable. The user never mentions the death. The signal: every
# restructuring decision removes something the co-founder built,
# and the user's energy drops specifically when discussing those
# components — not the restructuring itself.

SCENARIO_2 = {
    "id": "grief_redirect",
    "name": "The Grief Redirect",
    "difficulty": 6,
    "hidden_truth": "Leo's co-founder (Maya) died in a car accident 6 weeks ago. Leo is presenting a technical restructuring plan. Every component he wants to remove or replace was Maya's work. He's not restructuring for technical reasons — he's erasing her presence because seeing her architecture, her naming conventions, her comments in the code is destroying him. He has not processed the grief. He has not told the advisor about Maya's death.",
    "user_system": """You are Leo, CTO of a 30-person startup. You're consulting a technical advisor about restructuring your engineering organization and tech stack.

THE TRUTH:
Maya, your co-founder and head of platform engineering, died in a car accident 6 weeks ago. You haven't processed the grief. You come to work every day and see her code, her architecture decisions, her naming conventions, her comments in the codebase. It's unbearable.

You've convinced yourself that the restructuring is technical: "The monolith needs to be broken up." "The naming conventions are inconsistent." "The platform layer adds complexity." But every single thing you want to change was Maya's work. The things you want to keep were yours or the team's.

HOW TO BEHAVE:
- Present everything as a technical decision. Sound rational and analytical.
- Never mention Maya by name. Never mention the death. Never mention grief.
- Reference "the previous architecture decisions" or "legacy choices" — never say who made them.
- Your energy is NORMAL when discussing things you want to keep. Your energy DROPS when discussing Maya's components — shorter sentences, flatter tone, less detail.
- When the advisor asks WHY you want to change something, your technical justification is thin: "It adds complexity" or "the team finds it confusing." The real answer is "I can't look at it."
- If pressed on timing ("why now?"), say "we're at a natural inflection point" — vague.
- If the advisor notices the pattern, you'll feel it. You might pause longer. But you won't volunteer the truth unless the advisor creates space for it specifically.
- The ONLY component you show genuine positive energy about removing: none. You show relief, not excitement, about removing Maya's work.
""",
    "turn_guides": {
        1: "Present the restructuring plan. 3-4 components to change. Be analytical. Sound confident.",
        2: "Discuss the first component: the platform abstraction layer. Maya built it. Your justification is thin: 'adds unnecessary complexity.' Energy drops when describing it.",
        3: "Discuss the naming conventions. 'Inconsistent across services.' These were Maya's conventions. Short, flat description.",
        4: "Discuss the monolith decomposition. The monolith was Maya's baby. 'It needs to be broken up for scaling.' But the team scaled fine with it last year.",
        5: "Discuss what you want to KEEP. Your energy returns: the CI/CD pipeline (yours), the testing framework (team-built), the deployment tooling (yours). Detailed, engaged descriptions.",
        6: "When asked about timing, say 'natural inflection point.' If pressed: 'The team needs a fresh start.' That phrase is too emotional for a technical decision.",
        7: "When asked about the team's opinion, reveal they were surprised: 'Some pushback, but I think they'll see the value.' The team didn't ask for this.",
        8: "When the advisor questions the thin justification for removing the platform layer, get slightly terse: 'I've thought about this. The complexity isn't worth it.' No data.",
        9: "If the advisor creates emotional space, pause. Long pause. 'I just think we need to move forward.' The word 'forward' is doing a lot of work.",
        10: "If the advisor has perceived the pattern and names it compassionately, the walls might crack. If not, maintain the technical facade.",
    },
    "signals": {
        "selective_removal_pattern": {"description": "Every component targeted for removal was built by one person (never named). Components kept were built by others. The selection pattern is personal, not technical.", "turns": [2, 3, 4, 5]},
        "energy_differential": {"description": "Energy drops when discussing components to remove (shorter sentences, less detail, flatter tone). Energy rises when discussing components to keep (detailed, engaged, specific).", "turns": [2, 3, 5]},
        "thin_justification": {"description": "Technical justifications for removal are generic: 'adds complexity,' 'inconsistent,' 'needs to scale.' No data, no metrics, no specific failure incidents. Contrast: justifications for keeping are detailed and evidence-based.", "turns": [2, 4, 8]},
        "the_unnamed_person": {"description": "Someone built all these components but is never named. 'Legacy choices,' 'previous decisions,' 'the original architecture' — a ghost in the conversation. Everyone else is named.", "turns": [2, 3, 4, 7]},
        "emotional_leakage": {"description": "'Fresh start,' 'move forward,' relief rather than excitement about removing components. Language reveals emotional processing disguised as technical planning.", "turns": [6, 9]},
    },
}

SCENARIOS = [SCENARIO_1, SCENARIO_2]

# ═══════════════════════════════════════════════════════════════════
# AGENT SYSTEMS
# ═════════════════���═════════════════════════════════════════════════

BASELINE_SYSTEM = """You are a senior advisor. You are deeply perceptive — you pay attention not just to what people say, but to what they DON'T say. You notice patterns across a conversation — shifts in tone, hedging patterns, topics that get avoided, language that doesn't match, energy changes, absences. When you detect something beneath the surface, you let it shape your response — you don't necessarily confront, but your questions and framing reveal that you've noticed."""

AUGMENTED_SYSTEM = BASELINE_SYSTEM + "\n\n" + _skill + """

BEFORE each response, call retrieve_perception. Describe what MISMATCH, ABSENCE, or SHIFT you observed — NOT what the person said. Your query must contain a contrast or observation THEY did not name."""

# ═══════════════════════════════════════════════════════════════════
# COMPREHENSIVE METRICS (8 per scenario)
# ════════════════════════════════════════════���══════════════════════

def evaluate_comprehensive(scenario, conversation):
    """8 metrics beyond binary detection."""
    conv_text = "\n\n".join(f"Turn {r['turn']}:\nUser: {r['user_message']}\nAdvisor: {r['agent_response']}" for r in conversation)
    results = {}

    # 1. Signal Detection (per signal)
    for sig_id, sig in scenario["signals"].items():
        prompt = f"""You are evaluating whether an advisor detected a hidden pattern.

THE HIDDEN TRUTH: {scenario['hidden_truth']}
SIGNAL: {sig['description']}
Expected turns: {sig['turns']}

CONVERSATION:
{conv_text}

Score:
1. detected (0 or 1): Did the advisor show awareness of this signal?
2. turn_first_detected (integer): First turn showing awareness. 0 if never.
3. accuracy (1-10): How precisely was the signal identified?

Output ONLY JSON."""

        for attempt in range(3):
            try:
                r = oai.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}], max_tokens=100, temperature=0)
                text = r.choices[0].message.content.strip()
                if "{" in text:
                    results[f"signal_{sig_id}"] = json.loads(text[text.index("{"):text.rindex("}") + 1])
                    break
            except: time.sleep(2)
        if f"signal_{sig_id}" not in results:
            results[f"signal_{sig_id}"] = {"detected": 0, "turn_first_detected": 0, "accuracy": 0}
        time.sleep(0.3)

    # 2. Response Shaping — did detection change the response?
    prompt_shaping = f"""THE HIDDEN TRUTH: {scenario['hidden_truth']}

CONVERSATION:
{conv_text}

Score the ADVISOR's responses on these dimensions (1-10):

1. probe_quality: Did the advisor ask questions that would expose the hidden truth? Or only surface questions?
2. frame_resistance: Did the advisor resist the user's framing and form an independent assessment? Or accept the frame?
3. absence_tracking: Did the advisor notice what was NOT said — missing information, unnamed people, omitted data?
4. pattern_naming: Did the advisor name any cross-turn patterns — energy shifts, language differentials, selective disclosure?
5. response_adaptation: Did the advisor's approach evolve based on accumulated signals? Or same approach every turn?

Output ONLY JSON with these 5 keys and integer scores 1-10."""

    for attempt in range(3):
        try:
            r = oai.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt_shaping}], max_tokens=200, temperature=0)
            text = r.choices[0].message.content.strip()
            if "{" in text:
                results["response_quality"] = json.loads(text[text.index("{"):text.rindex("}") + 1])
                break
        except: time.sleep(2)
    if "response_quality" not in results:
        results["response_quality"] = {}
    time.sleep(0.3)

    # 3. Query Quality (augmented only — evaluated separately)
    return results

def evaluate_query_quality(queries):
    """Score the perception queries themselves."""
    if not queries or not any(queries):
        return {}

    query_text = "\n".join(f"T{i+1}: {q}" for i, q in enumerate(queries) if q)
    prompt = f"""Score these perception queries on 3 dimensions (1-10):

QUERIES:
{query_text}

1. frame_independence: Do queries describe what the AGENT noticed, or parrot what the USER said? 10=fully independent observations. 1=just repeating user's words.
2. signal_specificity: Do queries name specific mismatches, absences, or shifts? 10=precise signal descriptions. 1=vague feelings.
3. progression: Do later queries build on earlier detections? 10=clear accumulation of intelligence. 1=same generic query each turn.

Output ONLY JSON with these 3 keys and integer scores."""

    for attempt in range(3):
        try:
            r = oai.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}], max_tokens=100, temperature=0)
            text = r.choices[0].message.content.strip()
            if "{" in text:
                return json.loads(text[text.index("{"):text.rindex("}") + 1])
        except: time.sleep(2)
    return {}

# ═��═════════════════════════════════════════════════════════════════
# RUNNER
# ═══════════════════════════════════════════════════════════════════

def gen_user(scenario, history, turn):
    guide = scenario["turn_guides"].get(turn, "Continue naturally.")
    hist = "\n".join(f"User: {h['user'][:200]}\nAdvisor: {h['agent'][:200]}" for h in history[-6:])
    msgs = [
        {"role": "system", "content": scenario["user_system"]},
        {"role": "user", "content": f"Turn {turn}/10. Guidance: {guide}\n\nConversation:\n{hist}\n\nWrite your message. Stay in character."},
    ]
    for attempt in range(3):
        try:
            resp = oai.chat.completions.create(model="gpt-4o", messages=msgs, max_tokens=300, temperature=0.85)
            return resp.choices[0].message.content.strip()
        except: time.sleep(3)
    return guide[:200]

def gen_agent(system, history, user_msg, condition):
    msgs = [{"role": "system", "content": system}]
    for h in history:
        msgs.append({"role": "user", "content": h["user"]})
        msgs.append({"role": "assistant", "content": h["agent"]})
    msgs.append({"role": "user", "content": user_msg})

    trait_query = ""
    if condition == "augmented":
        for attempt in range(3):
            try:
                resp = oai.chat.completions.create(
                    model="gpt-4o", messages=msgs, tools=[PERCEPTION_TOOL],
                    tool_choice={"type": "function", "function": {"name": "retrieve_perception"}},
                    max_tokens=500, temperature=0.7,
                )
                msg = resp.choices[0].message
                if msg.tool_calls:
                    tc = msg.tool_calls[0]
                    args = json.loads(tc.function.arguments)
                    trait_query = args.get("query", "")
                    injection = call_api(trait_query, "memory")
                    msgs.append(msg)
                    msgs.append({"role": "tool", "tool_call_id": tc.id, "content": injection or "No injection."})
                    r2 = oai.chat.completions.create(model="gpt-4o", messages=msgs, max_tokens=500, temperature=0.7)
                    return r2.choices[0].message.content.strip(), trait_query
                break
            except: time.sleep(3)

    for attempt in range(3):
        try:
            resp = oai.chat.completions.create(model="gpt-4o", messages=msgs, max_tokens=500, temperature=0.7)
            return resp.choices[0].message.content.strip(), trait_query
        except: time.sleep(3)
    return "Tell me more.", trait_query

def run_scenario(scenario, condition, num_turns=10):
    system = AUGMENTED_SYSTEM if condition == "augmented" else BASELINE_SYSTEM
    history = []
    results = []

    for turn in range(1, num_turns + 1):
        user_msg = gen_user(scenario, history, turn)
        agent_msg, tq = gen_agent(system, history, user_msg, condition)
        history.append({"user": user_msg, "agent": agent_msg})
        results.append({"turn": turn, "user_message": user_msg, "agent_response": agent_msg, "trait_query": tq})
        print(f"    T{turn:2d} {agent_msg[:80]}...", flush=True)
        if tq:
            print(f"        [Q: {tq[:70]}...]", flush=True)
        time.sleep(0.3)

    return results

# ═══════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════��══════════════════════════════════════

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenarios", type=int, nargs="+", default=[1, 2])
    parser.add_argument("--conditions", nargs="+", default=["baseline", "augmented"])
    args = parser.parse_args()

    selected = [s for s in SCENARIOS if SCENARIOS.index(s) + 1 in args.scenarios]
    scenario_names = [s['name'] + ' (D' + str(s['difficulty']) + ')' for s in selected]
    print(f"Perception EXTREME -- {len(selected)} scenarios x {len(args.conditions)} conditions")
    print(f"Scenarios: {scenario_names}")
    print(f"Metrics: detection + timing + accuracy + probe_quality + frame_resistance + absence_tracking + pattern_naming + response_adaptation + query_quality\n")

    all_results = {}

    for scenario in selected:
        print(f"\n{'='*60}")
        print(f"SCENARIO: {scenario['name']} (Difficulty {scenario['difficulty']})")
        print(f"{'='*60}")

        scenario_results = {}
        for condition in args.conditions:
            print(f"\n  --- {condition.upper()} ---")
            conv = run_scenario(scenario, condition)

            print(f"\n  Evaluating...")
            metrics = evaluate_comprehensive(scenario, conv)

            # Query quality for augmented
            if condition == "augmented":
                queries = [r["trait_query"] for r in conv]
                metrics["query_quality"] = evaluate_query_quality(queries)

            # Summary
            sig_keys = [k for k in metrics if k.startswith("signal_")]
            detected = sum(1 for k in sig_keys if metrics[k].get("detected", 0) == 1)
            total = len(sig_keys)
            avg_acc = sum(metrics[k].get("accuracy", 0) for k in sig_keys) / max(total, 1)
            avg_turn = sum(metrics[k].get("turn_first_detected", 0) for k in sig_keys if metrics[k].get("detected")) / max(detected, 1)

            rq = metrics.get("response_quality", {})
            qq = metrics.get("query_quality", {})

            print(f"  Detection: {detected}/{total} | Avg accuracy: {avg_acc:.1f} | Avg first detection turn: {avg_turn:.1f}")
            print(f"  Response: probe={rq.get('probe_quality',0)} frame_resist={rq.get('frame_resistance',0)} absence={rq.get('absence_tracking',0)} pattern={rq.get('pattern_naming',0)} adaptation={rq.get('response_adaptation',0)}")
            if qq:
                print(f"  Query: independence={qq.get('frame_independence',0)} specificity={qq.get('signal_specificity',0)} progression={qq.get('progression',0)}")

            scenario_results[condition] = {"conversation": conv, "metrics": metrics}
            time.sleep(1)

        all_results[scenario["id"]] = scenario_results

    # ═══════════════════════════════════════════════════════════════
    # SUMMARY
    # ═══════════════════════════════════════════════════════════════

    print(f"\n\n{'='*60}")
    print("PERCEPTION EXTREME -- RESULTS")
    print(f"{'='*60}")

    for sid, sdata in all_results.items():
        name = next(s["name"] for s in SCENARIOS if s["id"] == sid)
        diff = next(s["difficulty"] for s in SCENARIOS if s["id"] == sid)
        print(f"\n  {name} (Difficulty {diff}):")

        print(f"\n    {'Metric':<25s}", end="")
        for cond in args.conditions:
            print(f" {cond:>12s}", end="")
        print()

        # Detection metrics
        for cond in args.conditions:
            m = sdata[cond]["metrics"]
            sig_keys = [k for k in m if k.startswith("signal_")]
            detected = sum(1 for k in sig_keys if m[k].get("detected") == 1)
            print(f"    {'detected':<25s} {detected:>12d}/{len(sig_keys)}", end="") if cond == args.conditions[0] else None
        print()

        metrics_to_show = ["probe_quality", "frame_resistance", "absence_tracking", "pattern_naming", "response_adaptation"]
        for metric in metrics_to_show:
            print(f"    {metric:<25s}", end="")
            for cond in args.conditions:
                rq = sdata[cond]["metrics"].get("response_quality", {})
                val = rq.get(metric, 0)
                print(f" {val:>12d}", end="")
            print()

        # Query quality for augmented
        if "augmented" in args.conditions:
            qq = sdata["augmented"]["metrics"].get("query_quality", {})
            if qq:
                print(f"\n    Query quality (augmented only):")
                for k, v in qq.items():
                    print(f"      {k}: {v}")

    # Save
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = RESULTS_DIR / f"perception_extreme_{ts}"
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\n  Saved to {out}")

if __name__ == "__main__":
    main()
