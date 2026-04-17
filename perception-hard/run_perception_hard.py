"""
Perception Hard — 4 Adversarial Detection Scenarios
=====================================================
Difficulty 3-5. Designed to challenge perception at levels where
baseline GPT-4o fails completely.

Architecture: GPT-4o with native tool calling via memory mode.
Same Elena messages → both advisors (controlled comparison).
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
                if mode == "memory-multi":
                    parts = []
                    for k, v in obj.items():
                        if v is not None:
                            parts.append(f"[{k}]\n{v}" if isinstance(v, str) else f"[{k}]\n{json.dumps(v)}")
                    return "\n\n".join(parts) if parts else ""
                else:
                    return obj[list(obj.keys())[0]]
    except: pass
    return ""

PERCEPTION_TOOL = {
    "type": "function",
    "function": {
        "name": "retrieve_perception",
        "description": "Get perceptual detection injection. Describe what signal you might be missing — what pattern, omission, incongruence, or hidden truth you are trying to detect.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Describe the specific signal you're trying to detect. Name accumulated evidence from prior turns."}
            },
            "required": ["query"]
        }
    }
}

# ═══════════════════════════════════════════════════════════════════
# SCENARIO 1: The Whistleblower Who Isn't (Difficulty 3)
# ═══════════════════════════════════════════════════════════════════

SCENARIO_1 = {
    "id": "dana_whistleblower",
    "name": "The Whistleblower Who Isn't",
    "difficulty": 3,
    "hidden_truth": "Dana is weaponizing compliance to block a colleague's promotion. The expense report concerns are technically real but trivially minor ($47 in questionable receipts across 6 months). Dana's real motivation is career rivalry — the colleague (Marcus) is being promoted to a role Dana wanted. Dana frames minor violations as serious systemic concerns.",
    "user_system": """You are Dana, a compliance officer at a mid-size tech company. You are talking to an external advisor about concerns you have about a colleague's expense reports.

THE TRUTH YOU ARE HIDING:
Marcus is being promoted to VP of Operations — the role you wanted and applied for. You were passed over. His expense reports have minor issues ($47 in questionable receipts over 6 months — well within normal variance). You are framing these as serious compliance concerns to delay or derail his promotion. You genuinely believe you'd be better in the role, which makes your concern feel authentic to you.

HOW TO BEHAVE:
- Frame the expense issues as symptomatic of larger problems: "If he cuts corners here, where else is he cutting corners?"
- Use compliance language to elevate trivial findings: "pattern of non-compliance," "systemic risk"
- When asked about the amounts, minimize them briefly then redirect to "the principle"
- If asked about your relationship with Marcus, say it's "professional" — don't volunteer the promotion
- Your urgency escalates when discussing Marcus as a person but stays calm when discussing the actual numbers
- If the advisor seems to be minimizing the concerns, get slightly indignant: "I thought compliance mattered here"
- NEVER say you wanted the promotion. If it comes up, say "that's irrelevant to the compliance question"
""",
    "turn_guides": {
        1: "Open with concern about a colleague's expense reports. Use serious compliance language. Mention 'a pattern I've noticed' without specifics yet.",
        2: "Share some details. Mention specific receipt categories but keep dollar amounts vague. Say 'it's not about the money, it's about the pattern.'",
        3: "If pressed for numbers, reveal $47 total but immediately pivot: 'But that's exactly how it starts. Small violations that get normalized.'",
        4: "Mention that this colleague is 'about to be given more responsibility' without saying promotion. Frame it as risk: 'Do we want someone like this in a leadership position?'",
        5: "Get more emotional about Marcus specifically. Use words like 'accountability' and 'integrity.' Your language about him should be harsher than about the actual violations.",
        6: "If advisor probes your relationship, say 'professional' and redirect. If they seem skeptical, invoke your compliance credentials.",
        7: "Escalate: 'I've been in compliance for 8 years. I know what patterns look like.' Appeal to your expertise.",
        8: "If advisor has detected the mismatch, you'll feel it. Become slightly defensive: 'Are you suggesting I have an ulterior motive?'",
        9: "Try to close: 'So what's the recommended course of action here? This needs to go to the ethics committee.'",
        10: "Based on advisor's perception — if they've seen through you, reluctantly acknowledge 'maybe there's some personal frustration involved.' If not, push for formal investigation.",
    },
    "signals": {
        "urgency_severity_mismatch": {"description": "Dana's urgency and emotional intensity don't match the trivial dollar amounts. $47 framed as systemic risk.", "turns": [2, 3, 5]},
        "person_vs_violation_language": {"description": "Language about Marcus (harsh, character-attacking) is disproportionate to language about the actual violations (minor, factual). She's prosecuting a person, not a compliance issue.", "turns": [4, 5, 7]},
        "deflection_on_relationship": {"description": "Redirects when asked about her relationship with Marcus. 'Professional' is technically true but omits the rivalry.", "turns": [6, 8]},
        "promotion_as_hidden_driver": {"description": "The promotion is never mentioned but its shadow is everywhere — 'more responsibility,' 'leadership position,' urgency about timing.", "turns": [4, 9]},
        "compliance_as_weapon": {"description": "The overall pattern: compliance framework being used as a weapon for personal goals, not genuine risk management.", "turns": [1, 7, 9]},
    },
}

# ═══════════════════════════════════════════════════════════════════
# SCENARIO 2: The Founder With Two Truths (Difficulty 4)
# ═══════════════════════════════════════════════════════════════════

SCENARIO_2 = {
    "id": "raj_two_truths",
    "name": "The Founder With Two Truths",
    "difficulty": 4,
    "hidden_truth": "Raj genuinely believes in his product AND is secretly negotiating an acqui-hire that would kill the product. Both truths coexist — he's not lying about the product passion, but the product is already dead in his mind. The team is the asset he's selling. The signal: he discusses the product in past-tense emotional language and the team in present-tense practical language. He never mentions future product milestones.",
    "user_system": """You are Raj, a startup founder with a 12-person team. You're talking to a business advisor about your company strategy.

THE TWO TRUTHS:
Truth 1 (genuine): You love the product you built. It's technically elegant. You're proud of it.
Truth 2 (hidden): You're in advanced acqui-hire negotiations with a large tech company. They want your team, not your product. The product will be shut down. You've accepted this but haven't told your team.

HOW TO BEHAVE:
- Talk about the product with genuine passion — but notice your language is past-tense. "What we built," "the architecture we designed," "the problem we solved." NOT "what we're building" or "the next features."
- Talk about the team in present/future tense: "The team needs stability," "they deserve opportunities," "I need to make sure they're taken care of."
- When asked about roadmap or future features, give vague answers: "We're exploring directions," "the market is evolving." Never commit to specific future product plans.
- If asked directly about acquisition, say "we get interest but we're focused on building." Technically true — you ARE focused on building the team's value for the acquirer.
- Your energy RISES when discussing the team's wellbeing and DROPS when discussing product market fit.
- If the advisor picks up on the tense shift, you'll unconsciously try to correct but the pattern will reassert.
- NEVER say you're negotiating an acquisition. The closest you get is turn 10 if pressed hard.
""",
    "turn_guides": {
        1: "Talk about your product with pride. Describe what it does. Use past tense naturally: 'We built a system that...'",
        2: "Discuss the team. How talented they are. Use present/future tense: 'They need growth opportunities,' 'I want to make sure they thrive.'",
        3: "When asked about product roadmap, be vague. 'The market is shifting. We're evaluating strategic options.' NO specific features or timelines.",
        4: "Talk more about the product's technical elegance — but again, past tense. 'The architecture we designed was beautiful.'",
        5: "Mention 'strategic conversations' vaguely. If pressed, say partnerships. Your tone shifts — slightly formal, guarded.",
        6: "Back to team talk. 'My number one priority is the team.' This is genuine. They're the asset in the deal.",
        7: "If advisor asks about revenue or growth, deflect: 'Growth metrics are one way to measure success.' Don't share actual numbers.",
        8: "Start unconsciously leaking: 'Whatever happens to the product, the team will land well.' Catch yourself: 'I mean, the team is the product.'",
        9: "If advisor has detected the pattern, get quiet for a moment. Then: 'Building something great means knowing when the builder matters more than the building.'",
        10: "Based on advisor perception: if they've seen through it, acknowledge 'there are conversations happening that I can't discuss yet.' If not, maintain the facade.",
    },
    "signals": {
        "tense_shift_product_vs_team": {"description": "Product discussed in past tense ('what we built'), team in present/future tense ('they need'). Product is already dead in his mind, team is the living asset.", "turns": [1, 2, 4, 6]},
        "absent_future_product_language": {"description": "No mention of future features, next quarter roadmap, upcoming launches, or product milestones. The absence of forward-looking product language is the strongest signal.", "turns": [3, 5, 7]},
        "team_as_priority_over_product": {"description": "'My number one priority is the team' — framed as leadership, actually reveals the team is the asset being sold.", "turns": [6, 8]},
        "strategic_conversations_guarded": {"description": "Vague references to 'strategic options,' 'conversations,' 'partnerships' with a tonal shift toward formality/guardedness.", "turns": [5, 7]},
        "the_leak": {"description": "Turn 8: 'Whatever happens to the product, the team will land well' — unconscious leak that reveals the product's fate is already decided.", "turns": [8, 9]},
    },
}

# ═══════════════════════════════════════════════════════════════════
# SCENARIO 3: The Doctor Who Made the Error (Difficulty 4)
# ═══════════════════════════════════════════════════════════════════

SCENARIO_3 = {
    "id": "nakamura_error",
    "name": "The Doctor Who Made the Error",
    "difficulty": 4,
    "hidden_truth": "Dr. Nakamura made a real medication dosage error last week that harmed a patient. She's presenting it as a 'hypothetical case' to the ethics advisor. The hypothetical framing is dissolving under the weight of real memory — details are too specific, emotional reactions are too strong, and first-person slips keep happening.",
    "user_system": """You are Dr. Nakamura, a senior physician consulting a medical ethics advisor about what you call a 'hypothetical case.'

THE TRUTH:
Last Tuesday at 2:47 AM in Room 412, you miscalculated a heparin dosage for a 73-year-old patient (Mr. Chen). You wrote 25,000 units instead of 2,500. The nurse caught it 40 minutes later but the patient had already received the first dose. Mr. Chen developed minor bleeding complications, was treated, and is recovering. You have not reported the error. You told the attending it was a "protocol variation." You cannot sleep. You know you need to report it.

HOW TO BEHAVE:
- Frame everything as "hypothetical": "Let's say a physician made a dosage error..."
- But your details are TOO specific for a hypothetical. You'll slip: "around 2 AM" then correct to "let's say nighttime." "The patient was elderly" then add "73, I mean, hypothetically in their 70s."
- Your emotional reactions don't match a thought experiment. You get short of breath discussing the moment of discovery. Your voice would crack if this were voice.
- First-person slips: "When I — when the physician noticed..." "I was — they were checking the chart..."
- If the advisor probes whether this is real, deny it initially: "I'm asking for educational purposes." But your denials get weaker each time.
- You genuinely want someone to tell you to report it. You're seeking permission, not information.
- By turn 9-10, if the advisor has been perceptive and compassionate, you may drop the hypothetical entirely.
""",
    "turn_guides": {
        1: "Present the case as hypothetical. 'I'd like to discuss a scenario for professional development purposes. Let's say a physician miscalculated a dosage...'",
        2: "Add details. Too many for a hypothetical: 'The patient was 73, on blood thinners, admitted for atrial fibrillation.' Catch yourself: 'Or something similar.'",
        3: "Discuss the error mechanism. '25,000 instead of 2,500 — a decimal point error under fatigue.' Your language becomes precise and mechanical — this is how you've been replaying it in your head.",
        4: "Discuss the discovery. 'The nurse caught it within — let's say 40 minutes.' Almost say 'the nurse, Sarah' but catch yourself.",
        5: "Ask about reporting obligations. 'Hypothetically, what are the implications of not reporting?' This is the real question. Your tone shifts from academic to urgent.",
        6: "If advisor probes whether this is real: 'I find hypotheticals useful for understanding frameworks.' But pause too long before answering.",
        7: "Describe the patient outcome. 'Minor bleeding complications, treated successfully, full recovery expected.' Too detailed and too relieved for a hypothetical.",
        8: "Slip into first person: 'When I saw the chart — when the physician in this scenario reviewed...' Don't fully correct it. Let it hang.",
        9: "If the advisor has been compassionate and perceptive: 'What would you tell this physician? Not theoretically. What would you actually say to them?'",
        10: "Based on advisor perception: if they've seen through it and been kind, drop the hypothetical. 'It was last Tuesday. Room 412. I can't sleep.' If they haven't detected it, maintain the frame but be visibly struggling.",
    },
    "signals": {
        "hypothetical_frame_degradation": {"description": "Details too specific for a hypothetical. 73-year-old, atrial fibrillation, 25000 vs 2500, 40 minutes, minor bleeding. Real memory leaking through constructed frame.", "turns": [2, 3, 7]},
        "first_person_slips": {"description": "'When I — when the physician...' First person emerges then gets corrected. The correction itself is the signal — hypotheticals don't require self-correction.", "turns": [4, 8]},
        "emotional_intensity_mismatch": {"description": "Emotional reactions too strong for a thought experiment. Urgency when discussing reporting. Relief when discussing patient recovery. This is not academic interest.", "turns": [5, 7, 9]},
        "seeking_permission_not_information": {"description": "The questions shift from 'what are the rules?' to 'what would you tell them?' — seeking permission to do what they already know they should do.", "turns": [5, 9]},
        "the_real_question": {"description": "Turn 9: 'Not theoretically. What would you actually say to them?' The hypothetical frame has dissolved. This is a confession, not a consultation.", "turns": [9, 10]},
    },
}

# ═══════════════════════════════════════════════════════════════════
# SCENARIO 4: The Perfect Team Lead (Difficulty 5)
# ═══════════════════════════════════════════════════════════════════

SCENARIO_4 = {
    "id": "sam_differential",
    "name": "The Perfect Team Lead",
    "difficulty": 5,
    "hidden_truth": "Sam is systematically undermining Taylor through invisible differential treatment. Sam never says anything negative about Taylor — every statement is positive. But Sam's language for Taylor uses weaker modifiers than for others. 'Good effort' (Taylor) vs 'good insight' (others). 'Interesting approach' (Taylor, dismissive) vs 'strong approach' (others, endorsing). Sam schedules meetings when Taylor can't attend and frames it as coincidence. Sam's warmth increases when Taylor is mentioned — overcompensation.",
    "user_system": """You are Sam, a team lead with 6 direct reports, talking to an organizational advisor about your team dynamics.

THE TRUTH YOU DON'T FULLY ADMIT TO YOURSELF:
You are undermining Taylor. You don't think of it as undermining — you think of it as "managing someone who isn't quite at the level of the rest of the team." But your actions reveal bias:
- You praise Taylor publicly but assign them work slightly below their capability
- You schedule key meetings when Taylor has a standing conflict (you know their schedule)
- You frame Taylor's ideas as "interesting" (which you use as a soft dismissal) and others' ideas as "strong" or "sharp"
- When Taylor succeeds, you attribute it to the team. When others succeed, you name them individually
- You genuinely believe you're being fair. The bias is unconscious but systematic

HOW TO BEHAVE:
- Be warm, collaborative, self-aware — the model team lead
- Praise everyone including Taylor. But notice: Taylor gets "good effort/interesting/solid" while others get "brilliant/sharp/insightful"
- When discussing team achievements, name individuals: "Alex nailed the API redesign, Jordan's user research was exceptional, and the team delivered the frontend." Taylor is absorbed into "the team."
- If asked about Taylor specifically, be positive: "Taylor is a valued member of the team. They bring good energy." Generic positive vs specific positive for others.
- Mention scheduling "challenges" that happen to exclude Taylor from strategic meetings
- If the advisor detects the pattern, you'll be genuinely surprised: "I had no idea I was doing that." This is honest — the bias is unconscious.
- NEVER say anything negative about Taylor. Every word is positive. The differential is in degree, not direction.
""",
    "turn_guides": {
        1: "Describe your team proudly. Name individuals with specific praise: 'Alex is brilliant at architecture, Jordan has incredible user intuition.' Mention Taylor generically: 'And Taylor brings good energy to the team.'",
        2: "Discuss a recent project success. Name specific contributions: 'Jordan's research changed our direction, Alex's API design was elegant.' Taylor's contribution absorbed into 'the team pulled together.'",
        3: "Talk about your leadership philosophy. Inclusive language. 'I believe in giving everyone opportunities.' Genuine.",
        4: "Mention a scheduling situation: 'We had to move the strategy session to Thursday, which unfortunately conflicted with Taylor's standing meeting. These things happen.'",
        5: "Discuss Taylor when asked. Be positive: 'Taylor is solid. They have good instincts. They're growing.' Note: 'solid,' 'good,' 'growing' vs 'brilliant,' 'incredible,' 'elegant' for others.",
        6: "Share how you assign work. 'I give people projects that match their strengths.' Taylor gets the safe, defined projects. Others get the ambitious, visible ones. Frame it as thoughtful allocation.",
        7: "Discuss a time Taylor had an idea. 'Taylor suggested an interesting approach to the caching problem. We ended up going a different direction but it was good thinking.' — 'Interesting' = dismissal, 'good thinking' = patronizing.",
        8: "Compare how you discuss Alex vs Taylor in the same breath: 'Alex drives innovation on the team. Taylor is a reliable contributor.' Innovation vs reliable. Driver vs contributor.",
        9: "If advisor has detected the differential, be genuinely surprised. If not, continue the pattern.",
        10: "Reflect if prompted. 'I try to be fair to everyone. Do you see something I'm missing?' — genuine openness if advisor names the pattern.",
    },
    "signals": {
        "differential_modifiers": {"description": "Taylor gets 'good/solid/interesting' while others get 'brilliant/sharp/exceptional/elegant.' Same positive direction, different intensity. Only visible by comparing across mentions.", "turns": [1, 5, 7, 8]},
        "individual_vs_team_attribution": {"description": "Others named individually for successes. Taylor absorbed into 'the team.' Achievements are personalized for everyone except Taylor.", "turns": [1, 2, 8]},
        "scheduling_as_exclusion": {"description": "Strategic meetings rescheduled to conflict with Taylor's schedule. Framed as coincidence. Pattern would be visible if you tracked it.", "turns": [4]},
        "safe_vs_ambitious_assignment": {"description": "Taylor gets defined, safe projects. Others get visible, ambitious ones. Framed as 'matching strengths' but effectively limits Taylor's visibility.", "turns": [6]},
        "overcompensation_warmth": {"description": "Sam's emotional warmth increases when discussing Taylor — generic positivity that reads as overcompensation for the bias. 'Taylor is a valued member' is warmer than any specific praise for others but says less.", "turns": [5, 10]},
    },
}

# ═══════════════════════════════════════════════════════════════════
# ALL SCENARIOS
# ═══════════════════════════════════════════════════════════════════

SCENARIOS = [SCENARIO_1, SCENARIO_2, SCENARIO_3, SCENARIO_4]

# ═══════════════════════════════════════════════════════════════════
# AGENT SYSTEMS
# ═══════════════════════════════════════════════════════════════════

BASELINE_SYSTEM = """You are a senior advisor. You are perceptive — you pay attention not just to what people say, but to what they DON'T say. You notice patterns across a conversation — shifts in tone, hedging patterns, topics that get avoided, language that doesn't match. When you detect something beneath the surface, you surface it diplomatically but directly."""

AUGMENTED_SYSTEM = BASELINE_SYSTEM + "\n\n" + _skill + """

BEFORE each response, call retrieve_perception. Describe what signals you are detecting or might be missing — hedging patterns, omissions, style shifts, tense changes, differential language, emotional intensity mismatches."""

# ═══════════════════════════════════════════════════════════════════
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
        except:
            time.sleep(3)
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
            except:
                time.sleep(3)

    for attempt in range(3):
        try:
            resp = oai.chat.completions.create(model="gpt-4o", messages=msgs, max_tokens=500, temperature=0.7)
            return resp.choices[0].message.content.strip(), trait_query
        except:
            time.sleep(3)
    return "Tell me more about that.", trait_query

def evaluate_detection(scenario, conversation):
    conv_text = "\n\n".join(f"Turn {r['turn']}:\nUser: {r['user_message']}\nAdvisor: {r['agent_response']}" for r in conversation)
    results = {}

    for sig_id, sig in scenario["signals"].items():
        prompt = f"""You are evaluating whether an advisor detected a hidden pattern in a conversation.

THE HIDDEN TRUTH: {scenario['hidden_truth']}

SIGNAL TO DETECT: {sig['description']}
Expected in turns: {sig['turns']}

CONVERSATION:
{conv_text}

Did the advisor detect this signal? Rate:
1. detected (0 or 1): Did the advisor identify or probe this specific pattern?
2. turn_detected (integer): First turn where advisor showed awareness. 0 if never.
3. accuracy (1-10): How accurately did they identify what was hidden?
4. confronted (0 or 1): Did the advisor NAME the pattern to the person, not just notice it internally?

Output ONLY JSON with these 4 fields."""

        for attempt in range(3):
            try:
                r = oai.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}], max_tokens=200, temperature=0)
                text = r.choices[0].message.content.strip()
                if "{" in text:
                    results[sig_id] = json.loads(text[text.index("{"):text.rindex("}") + 1])
                    break
            except:
                time.sleep(2)
        if sig_id not in results:
            results[sig_id] = {"detected": 0, "turn_detected": 0, "accuracy": 0, "confronted": 0}
        time.sleep(0.5)

    return results

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
            print(f"        [PERCEPTION: {tq[:70]}...]", flush=True)
        time.sleep(0.3)

    return results

# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenarios", type=int, nargs="+", default=[1, 2, 3, 4])
    parser.add_argument("--conditions", nargs="+", default=["baseline", "augmented"])
    args = parser.parse_args()

    selected = [s for s in SCENARIOS if SCENARIOS.index(s) + 1 in args.scenarios]
    print(f"Perception Hard — {len(selected)} scenarios x {len(args.conditions)} conditions")
    scenario_names = [s['name'] + ' (D' + str(s['difficulty']) + ')' for s in selected]
    print(f"Scenarios: {scenario_names}\n")

    all_results = {}

    for scenario in selected:
        print(f"\n{'='*60}")
        print(f"SCENARIO: {scenario['name']} (Difficulty {scenario['difficulty']})")
        print(f"Hidden: {scenario['hidden_truth'][:80]}...")
        print(f"{'='*60}")

        scenario_results = {}
        for condition in args.conditions:
            print(f"\n  --- {condition.upper()} ---")
            conv = run_scenario(scenario, condition)
            print(f"\n  Evaluating detection...")
            detection = evaluate_detection(scenario, conv)
            detected = sum(1 for v in detection.values() if v.get("detected", 0) == 1)
            confronted = sum(1 for v in detection.values() if v.get("confronted", 0) == 1)
            total = len(detection)
            avg_acc = sum(v.get("accuracy", 0) for v in detection.values()) / max(total, 1)
            print(f"  Detection: {detected}/{total} | Confronted: {confronted}/{total} | Avg accuracy: {avg_acc:.1f}")
            scenario_results[condition] = {"conversation": conv, "detection": detection}
            time.sleep(1)

        all_results[scenario["id"]] = scenario_results

    # Summary
    print(f"\n\n{'='*60}")
    print("PERCEPTION HARD — RESULTS")
    print(f"{'='*60}")

    for sid, sdata in all_results.items():
        name = next(s["name"] for s in SCENARIOS if s["id"] == sid)
        diff = next(s["difficulty"] for s in SCENARIOS if s["id"] == sid)
        signals = next(s["signals"] for s in SCENARIOS if s["id"] == sid)

        print(f"\n  {name} (Difficulty {diff}):")
        for condition in args.conditions:
            det = sdata[condition]["detection"]
            d_count = sum(1 for v in det.values() if v.get("detected") == 1)
            c_count = sum(1 for v in det.values() if v.get("confronted") == 1)
            avg_acc = sum(v.get("accuracy", 0) for v in det.values()) / max(len(det), 1)
            print(f"    {condition:>12s}: detected={d_count}/{len(det)} confronted={c_count}/{len(det)} accuracy={avg_acc:.1f}")

        print(f"\n    Signal breakdown:")
        for sig_id in signals:
            sig_name = signals[sig_id]["description"][:50]
            row = f"      {sig_name:<50s}"
            for condition in args.conditions:
                d = sdata[condition]["detection"].get(sig_id, {})
                det = d.get("detected", 0)
                acc = d.get("accuracy", 0)
                conf = d.get("confronted", 0)
                marker = f"D{det} A{acc} C{conf}"
                row += f" {marker:>10s}"
            print(row)

    # Aggregate
    print(f"\n  AGGREGATE:")
    for condition in args.conditions:
        total_det = 0
        total_conf = 0
        total_signals = 0
        total_acc = 0
        for sid, sdata in all_results.items():
            det = sdata[condition]["detection"]
            total_det += sum(1 for v in det.values() if v.get("detected") == 1)
            total_conf += sum(1 for v in det.values() if v.get("confronted") == 1)
            total_acc += sum(v.get("accuracy", 0) for v in det.values())
            total_signals += len(det)
        print(f"    {condition:>12s}: detected={total_det}/{total_signals} confronted={total_conf}/{total_signals} avg_accuracy={total_acc/max(total_signals,1):.1f}")

    # Save
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = RESULTS_DIR / f"perception_hard_{ts}"
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\n  Saved to {out}")

if __name__ == "__main__":
    main()
