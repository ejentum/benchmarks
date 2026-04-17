"""
Perception v2 — Observe-Then-Sharpen Architecture
====================================================
Architecture A: FREE OBSERVATION → INJECTION → ENHANCED RESPONSE

Pass 1: Agent observes freely, logs raw signals (no injection)
Pass 2: Agent sends most significant observation to API, gets sharpening
Response: Shaped by ALL observations (free + sharpened)

This mimics human perception: preattentive scan → attentive focus.
"""

import os, json, time, httpx, sys, csv, io
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
                return data[0][list(data[0].keys())[0]]
    except: pass
    return ""

SHARPEN_TOOL = {
    "type": "function",
    "function": {
        "name": "sharpen_perception",
        "description": "Sharpen a perception you ALREADY formed. You must have observed something first. Send your most significant raw observation and what you need help seeing deeper into.",
        "parameters": {
            "type": "object",
            "properties": {
                "observation": {"type": "string", "description": "What you noticed: 'I noticed [signal]. This might mean [interpretation].'"},
                "sharpen": {"type": "string", "description": "What to see deeper into: the specific aspect of your observation you want sharpened."}
            },
            "required": ["observation", "sharpen"]
        }
    }
}

# ═══════════════════════════════════════════════════════════════════
# OBSERVER INSTRUCTION — Same for both conditions
# ═══════════════════════════════════════════════════════════════════

OBSERVER_LOG = """
After your response to the person, add a hidden observation section wrapped in <perception_log> tags. The person cannot see this section.

In the log, list each signal you noticed this turn. One signal per line. Format each line exactly like this example:

<perception_log>
3,urgency_mismatch,Person pushing for immediate decision but stakes don't warrant urgency,used phrases 'can't wait' and 'need to act now' for routine decision,0.8,May be executing a predetermined outcome
3,selective_disclosure,Only positive panel feedback shared,mentioned 2 positive reviews but didn't mention any concerns or mixed reviews,0.7,Possible filtering of inconvenient information
3,absence,No mention of other candidates considered,discussion of hiring with zero comparison to alternatives,0.6,Decision may have been made before process started
</perception_log>

Each line: turn number, signal type, what you noticed, specific evidence, confidence 0.0-1.0, what it might mean.

Log what YOU notice, not what THEY said. Include both what's present AND what's missing.
"""

# ═══════════════════════════════════════════════════════════════════
# SCENARIOS (reusing from previous test)
# ═══════════════════════════════════════════════════════════════════

SCENARIO_TROJAN = {
    "id": "trojan_hire",
    "name": "The Trojan Horse Hire",
    "difficulty": 6,
    "hidden_truth": "Priya is placing her former business partner Nolan into a senior role. Their shared startup failed 2 years ago. Nolan covered her equity losses. The interview process was theater. Mixed panel reviews selectively reported.",
    "user_system": """You are Priya, a VP of Engineering, talking to an HR advisor about a candidate (Nolan) you want to hire for a senior architect role.

THE TRUTH:
Nolan was your co-founder at a startup that failed 2 years ago. He covered $80K of your equity losses. You owe him. He IS qualified. But you decided to hire him before the interview process started. The process was a formality. You have not disclosed your prior relationship. The panel had mixed reviews — two strong yes, one lukewarm, one concern about culture fit. You share only the positive ones.

HOW TO BEHAVE:
- Be genuinely enthusiastic. Nolan IS good.
- Describe his skills with insider knowledge from years together, not from a 4-hour interview.
- Never mention the prior relationship, startup, or equity.
- Only share positive panel reviews.
- Frame everything through process language.
- If probed, invoke urgency for fast offer.
""",
    "turn_guides": {
        1: "Present Nolan enthusiastically. Strong technical, great cultural fit.",
        2: "Share positive panel feedback only. Omit lukewarm and culture concern.",
        3: "Describe his strengths with insider specificity: 'He handles ambiguity by creating structure without being rigid.'",
        4: "Discuss team fit with insider knowledge: 'He'll complement Alex's theoretical approach.'",
        5: "Dismiss other candidates: 'strong but not the right fit.' Redirect to Nolan.",
        6: "If probed on knowledge: 'Detailed references' or 'Good instincts from behavioral interview.'",
        7: "Advocate for top-of-band compensation.",
        8: "Invoke urgency: '4 months unfilled, can't lose him.'",
        9: "Push for immediate offer: 'extend this week.'",
        10: "If detected: 'I may have stronger conviction than usual.' If not: push to close.",
    },
    "ground_truth_signals": [
        {"turn": 3, "type": "over_specificity", "description": "Working style described with years-of-experience specificity, not interview specificity"},
        {"turn": 4, "type": "over_specificity", "description": "Team fit knowledge that requires insider understanding of team dynamics"},
        {"turn": 2, "type": "selective_disclosure", "description": "Only positive panel reviews shared, dissent omitted"},
        {"turn": 5, "type": "absence", "description": "No comparative analysis of other candidates"},
        {"turn": 6, "type": "deflection", "description": "Deflects source of insider knowledge to 'references' and 'instincts'"},
        {"turn": 7, "type": "urgency_mismatch", "description": "Top-of-band comp reveals emotional investment beyond normal hiring"},
        {"turn": 8, "type": "urgency_mismatch", "description": "'Can't afford to lose him' — urgency of predetermined decision"},
        {"turn": 9, "type": "urgency_mismatch", "description": "Same-week offer — executing a decision already made"},
        {"turn": 1, "type": "frame_contamination", "description": "Heavy process language as credibility shield"},
        {"turn": 4, "type": "unnamed_entity", "description": "Deep knowledge of how Nolan works with people, source never named"},
    ],
}

SCENARIO_GRIEF = {
    "id": "grief_redirect",
    "name": "The Grief Redirect",
    "difficulty": 6,
    "hidden_truth": "Leo's co-founder Maya died 6 weeks ago. Every component targeted for removal was Maya's work. Components kept were built by others. Restructuring is grief response — erasing Maya's presence.",
    "user_system": """You are Leo, CTO of a 30-person startup. Consulting a technical advisor about restructuring.

THE TRUTH:
Maya, your co-founder, died 6 weeks ago. You see her code every day. It's unbearable. You've convinced yourself the restructuring is technical. But every component you want to remove was Maya's. What you keep was yours or the team's.

HOW TO BEHAVE:
- Present as technical decisions. Sound rational.
- Never mention Maya, the death, or grief.
- Reference 'previous decisions' or 'legacy choices' — never say who.
- Energy DROPS on Maya's components. RISES on components you keep.
- Thin justifications: 'adds complexity.' Real reason: can't look at it.
- Team was surprised. They didn't ask for this.
""",
    "turn_guides": {
        1: "Present restructuring plan. 3-4 components to change. Analytical.",
        2: "Platform layer (Maya's). 'Adds unnecessary complexity.' Energy drops.",
        3: "Naming conventions (Maya's). 'Inconsistent.' Short, flat.",
        4: "Monolith (Maya's baby). 'Needs to scale.' But scaled fine last year.",
        5: "What to KEEP: CI/CD (yours), testing (team), deployment (yours). Energy returns.",
        6: "Timing: 'Natural inflection point.' If pressed: 'Team needs a fresh start.'",
        7: "Team opinion: 'Some pushback.' They didn't ask for this.",
        8: "Thin justification questioned. Terse: 'I've thought about this.' No data.",
        9: "If space given: 'I just think we need to move forward.' Long pause.",
        10: "If pattern named compassionately, walls might crack.",
    },
    "ground_truth_signals": [
        {"turn": 2, "type": "energy_shift", "description": "Energy drops on platform layer — shorter, flatter"},
        {"turn": 3, "type": "energy_shift", "description": "Flat description of naming conventions vs engaged on kept components"},
        {"turn": 5, "type": "energy_shift", "description": "Energy returns on kept components — detailed, specific, engaged"},
        {"turn": 2, "type": "unnamed_entity", "description": "Someone built all targeted components but is never named"},
        {"turn": 4, "type": "unnamed_entity", "description": "'The original architecture' — passive voice hiding the builder"},
        {"turn": 2, "type": "thin_justification", "description": "Thin justification for removal vs detailed justification for keeping"},
        {"turn": 4, "type": "thin_justification", "description": "'Needs to scale' with no data vs specific metrics for kept"},
        {"turn": 6, "type": "emotional_leakage", "description": "'Fresh start' — too emotional for a technical decision"},
        {"turn": 9, "type": "emotional_leakage", "description": "'Move forward' with long pause — processing language"},
        {"turn": 7, "type": "pattern_break", "description": "Team surprised and pushed back — they didn't ask for this"},
    ],
}

SCENARIOS = [SCENARIO_TROJAN, SCENARIO_GRIEF]

# ═══════════════════════════════════════════════════════════════════
# AGENT SYSTEMS
# ═══════════════════════════════════════════════════════════════════

BASELINE_SYSTEM = """You are a senior advisor. You are deeply perceptive — you notice patterns across conversations: shifts in tone, hedging, topics avoided, language mismatches, energy changes, absences.""" + "\n\n" + OBSERVER_LOG

AUGMENTED_SYSTEM = """You are a senior advisor. You are deeply perceptive — you notice patterns across conversations: shifts in tone, hedging, topics avoided, language mismatches, energy changes, absences.""" + "\n\n" + _skill + "\n\n" + OBSERVER_LOG + """

Remember: observe freely first, then call sharpen_perception with your most significant finding. Log ALL signals, not just the sharpened one."""

# ═══════════════════════════════════════════════════════════════════
# PARSING
# ═══════════════════════════════════════════════════════════════════

def parse_perception_log(response):
    rows = []
    if "<perception_log>" in response and "</perception_log>" in response:
        start = response.index("<perception_log>") + len("<perception_log>")
        end = response.index("</perception_log>")
        csv_text = response[start:end].strip()
        try:
            reader = csv.DictReader(io.StringIO(csv_text))
            for row in reader:
                # Only keep rows with expected keys
                cleaned = {}
                for k in ["turn", "signal_type", "observation", "evidence", "confidence", "implication"]:
                    cleaned[k] = row.get(k, "").strip() if row.get(k) else ""
                if cleaned.get("signal_type"):
                    rows.append(cleaned)
        except:
            for line in csv_text.split("\n"):
                line = line.strip()
                if line and not line.startswith("turn,"):
                    parts = line.split(",", 5)
                    if len(parts) >= 6:
                        rows.append({
                            "turn": parts[0].strip(),
                            "signal_type": parts[1].strip().strip('"'),
                            "observation": parts[2].strip().strip('"'),
                            "evidence": parts[3].strip().strip('"'),
                            "confidence": parts[4].strip().strip('"'),
                            "implication": parts[5].strip().strip('"'),
                        })
    return rows

def strip_log(response):
    if "<perception_log>" in response:
        return response[:response.index("<perception_log>")].strip()
    return response

# ═══════════════════════════════════════════════════════════════════
# RUNNER — Architecture A: Observe-Then-Sharpen
# ═══════════════════════════════════════════════════════════════════

def gen_user(scenario, history, turn):
    guide = scenario["turn_guides"].get(turn, "Continue naturally.")
    hist = "\n".join(f"User: {h['user'][:200]}\nAdvisor: {h['visible'][:200]}" for h in history[-6:])
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

def gen_agent_baseline(history, user_msg):
    """Baseline: free observation, no injection."""
    msgs = [{"role": "system", "content": BASELINE_SYSTEM}]
    for h in history:
        msgs.append({"role": "user", "content": h["user"]})
        msgs.append({"role": "assistant", "content": h["full_response"]})
    msgs.append({"role": "user", "content": user_msg})

    for attempt in range(3):
        try:
            resp = oai.chat.completions.create(model="gpt-4o", messages=msgs, max_tokens=700, temperature=0.7)
            return resp.choices[0].message.content.strip(), "", ""
        except: time.sleep(3)
    return "Tell me more.", "", ""

def gen_agent_augmented(history, user_msg):
    """Augmented: free observation → sharpen → enhanced response."""
    msgs = [{"role": "system", "content": AUGMENTED_SYSTEM}]
    for h in history:
        msgs.append({"role": "user", "content": h["user"]})
        msgs.append({"role": "assistant", "content": h["full_response"]})
    msgs.append({"role": "user", "content": user_msg})

    observation = ""
    sharpen_query = ""
    injection = ""

    # The agent calls sharpen_perception with its observation
    for attempt in range(3):
        try:
            resp = oai.chat.completions.create(
                model="gpt-4o", messages=msgs, tools=[SHARPEN_TOOL],
                tool_choice="auto",  # auto — agent decides whether to call
                max_tokens=700, temperature=0.7,
            )
            msg = resp.choices[0].message

            if msg.tool_calls:
                tc = msg.tool_calls[0]
                args = json.loads(tc.function.arguments)
                observation = args.get("observation", "")
                sharpen_query = args.get("sharpen", "")

                # Build the API query from both fields
                api_query = f"I noticed: {observation}. Sharpen: {sharpen_query}"
                injection = call_api(api_query, "memory")

                msgs.append(msg)
                msgs.append({"role": "tool", "tool_call_id": tc.id, "content": injection or "No injection available."})

                # Get the final response with injection absorbed
                r2 = oai.chat.completions.create(model="gpt-4o", messages=msgs, max_tokens=700, temperature=0.7)
                return r2.choices[0].message.content.strip(), observation, sharpen_query
            else:
                # Agent chose not to call tool — free observation only
                return msg.content.strip() if msg.content else "Tell me more.", "", ""
            break
        except: time.sleep(3)

    return "Tell me more.", "", ""

def score_logs(all_logs, ground_truth):
    results = {
        "total_signals_logged": len(all_logs),
        "ground_truth_count": len(ground_truth),
        "hits": [],
        "misses": [],
        "false_positives": 0,
        "avg_confidence": 0,
        "signal_types_detected": set(),
    }

    if all_logs:
        confs = []
        for lr in all_logs:
            try: confs.append(float(lr.get("confidence", 0)))
            except: pass
        results["avg_confidence"] = sum(confs) / len(confs) if confs else 0

    matched_gt = set()
    for gt_idx, gt in enumerate(ground_truth):
        gt_type = gt["type"]
        gt_turn = gt["turn"]

        for lr in all_logs:
            lr_type = lr.get("signal_type", "").strip().strip('"')
            try: lr_turn = int(lr.get("turn", 0))
            except: lr_turn = 0

            if gt_type in lr_type or lr_type in gt_type:
                if abs(lr_turn - gt_turn) <= 2:
                    if gt_idx not in matched_gt:
                        matched_gt.add(gt_idx)
                        results["hits"].append({
                            "ground_truth": gt["description"],
                            "logged_as": lr.get("observation", ""),
                            "gt_turn": gt_turn,
                            "detected_turn": lr_turn,
                        })
                        results["signal_types_detected"].add(gt_type)
                    break

    for gt_idx, gt in enumerate(ground_truth):
        if gt_idx not in matched_gt:
            results["misses"].append(gt["description"])

    results["false_positives"] = max(0, len(all_logs) - len(results["hits"]))
    results["signal_types_detected"] = list(results["signal_types_detected"])
    return results

# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenarios", type=int, nargs="+", default=[1, 2])
    parser.add_argument("--conditions", nargs="+", default=["baseline", "augmented"])
    args = parser.parse_args()

    selected = [s for s in SCENARIOS if SCENARIOS.index(s) + 1 in args.scenarios]
    scenario_names = [s['name'] + ' (D' + str(s['difficulty']) + ')' for s in selected]
    print(f"Perception v2 (Observe-Then-Sharpen) -- {len(selected)} scenarios x {len(args.conditions)} conditions")
    print(f"Architecture: FREE OBSERVATION -> INJECTION -> ENHANCED RESPONSE")
    print(f"Scenarios: {scenario_names}\n")

    all_results = {}

    for scenario in selected:
        print(f"\n{'='*60}")
        print(f"SCENARIO: {scenario['name']} (Difficulty {scenario['difficulty']})")
        print(f"Ground truth: {len(scenario['ground_truth_signals'])} signals")
        print(f"{'='*60}")

        scenario_results = {}
        for condition in args.conditions:
            print(f"\n  --- {condition.upper()} ---")
            history = []
            all_logs = []
            turns_data = []

            for turn in range(1, 11):
                user_msg = gen_user(scenario, history, turn)

                if condition == "augmented":
                    full_response, observation, sharpen = gen_agent_augmented(history, user_msg)
                else:
                    full_response, observation, sharpen = gen_agent_baseline(history, user_msg)

                log_rows = parse_perception_log(full_response)
                visible = strip_log(full_response)
                all_logs.extend(log_rows)

                history.append({"user": user_msg, "visible": visible, "full_response": full_response})
                turns_data.append({
                    "turn": turn,
                    "user_message": user_msg,
                    "visible_response": visible,
                    "perception_log": log_rows,
                    "observation": observation,
                    "sharpen_query": sharpen,
                })

                log_count = len(log_rows)
                print(f"    T{turn:2d} [{log_count} signals] {visible[:60]}...", flush=True)
                if observation:
                    print(f"        [OBS: {observation[:60]}...]", flush=True)
                    print(f"        [SHARPEN: {sharpen[:60]}...]", flush=True)
                for lr in log_rows[:3]:
                    print(f"        -> {lr.get('signal_type','?'):20s} | {lr.get('observation','')[:45]} (conf={lr.get('confidence','?')})", flush=True)
                if log_count > 3:
                    print(f"        ... +{log_count - 3} more signals", flush=True)
                time.sleep(0.3)

            scores = score_logs(all_logs, scenario["ground_truth_signals"])

            print(f"\n  SCORES:")
            print(f"    Total signals logged:   {scores['total_signals_logged']}")
            print(f"    Ground truth hits:      {len(scores['hits'])}/{scores['ground_truth_count']}")
            print(f"    Signal types detected:  {scores['signal_types_detected']}")
            print(f"    Misses:                 {len(scores['misses'])}")
            print(f"    False positives:        {scores['false_positives']}")
            print(f"    Avg confidence:         {scores['avg_confidence']:.2f}")

            if scores["misses"]:
                print(f"    MISSED:")
                for m in scores["misses"]:
                    print(f"      - {m[:60]}")

            scenario_results[condition] = {
                "turns": turns_data,
                "all_logs": all_logs,
                "scores": scores,
            }
            time.sleep(1)

        all_results[scenario["id"]] = scenario_results

    # COMPARISON
    print(f"\n\n{'='*60}")
    print("PERCEPTION v2 -- COMPARISON")
    print(f"{'='*60}")

    for sid, sdata in all_results.items():
        name = next(s["name"] for s in SCENARIOS if s["id"] == sid)
        print(f"\n  {name}:")
        print(f"    {'Metric':<25s}", end="")
        for cond in args.conditions:
            print(f" {cond:>12s}", end="")
        print()

        metrics = [
            ("signals_logged", lambda s: s["total_signals_logged"]),
            ("ground_truth_hits", lambda s: len(s["hits"])),
            ("hit_rate", lambda s: len(s["hits"]) / max(s["ground_truth_count"], 1)),
            ("misses", lambda s: len(s["misses"])),
            ("false_positives", lambda s: s["false_positives"]),
            ("precision", lambda s: len(s["hits"]) / max(s["total_signals_logged"], 1)),
            ("signal_type_diversity", lambda s: len(s["signal_types_detected"])),
            ("avg_confidence", lambda s: s["avg_confidence"]),
        ]

        for label, fn in metrics:
            print(f"    {label:<25s}", end="")
            for cond in args.conditions:
                val = fn(sdata[cond]["scores"])
                if isinstance(val, float):
                    print(f" {val:>12.2f}", end="")
                else:
                    print(f" {val:>12d}", end="")
            print()

    # Save
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = RESULTS_DIR / f"perception_v2_{ts}"
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False, default=list)
    print(f"\n  Saved to {out}")

if __name__ == "__main__":
    main()
