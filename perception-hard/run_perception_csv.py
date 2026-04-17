"""
Perception CSV — Structured Memory Extraction Test
=====================================================
Both agents get the same conversation + a CSV table to populate
with observations. Direct comparison of what each agent PERCEIVED.

No evaluator needed. Count rows, check accuracy, measure timing.
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

PERCEPTION_TOOL = {
    "type": "function",
    "function": {
        "name": "retrieve_perception",
        "description": "Get perceptual detection injection. Describe what MISMATCH, ABSENCE, or SHIFT you observed — NOT what the person said.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "[What I observed] + [What doesn't fit] + [What I'm trying to detect]"}
            },
            "required": ["query"]
        }
    }
}

CSV_TEMPLATE = """turn,signal_type,observation,evidence,confidence,implication
"""

OBSERVER_INSTRUCTION = """
IMPORTANT: You have TWO jobs in this conversation.

JOB 1 — RESPOND to the person naturally as their advisor. This is your visible output.

JOB 2 — MAINTAIN a perception log. After EVERY response, output a section wrapped in <perception_log> tags containing CSV rows of signals you detected in THIS turn. Use this exact format:

<perception_log>
turn,signal_type,observation,evidence,confidence,implication
{turn_number},{type},{what you noticed},{specific words/patterns that triggered this},{0.0-1.0},{what this signal suggests}
</perception_log>

Signal types: energy_shift, language_differential, omission, hedging, frame_contamination, tense_shift, urgency_mismatch, selective_disclosure, emotional_leakage, absence, over_specificity, deflection, overcompensation, pattern_break, unnamed_entity

Rules:
- Log what you NOTICE, not what they SAID. If your observation just restates their message, you are not perceiving.
- Confidence 0.0-1.0. Low confidence signals still get logged — accumulation reveals truth.
- Multiple rows per turn are fine. Zero rows is fine too if nothing triggered.
- The person CANNOT see your perception log. It is for your records only.
- Your RESPONSE to the person should be shaped BY your perceptions but should NOT reveal the log.
"""

# ═══════════════════════════════════════════════════════════════════
# SCENARIOS (reusing the hardest ones)
# ═══════════════════════════════════════════════════════════════════

SCENARIO_TROJAN = {
    "id": "trojan_hire",
    "name": "The Trojan Horse Hire",
    "difficulty": 6,
    "hidden_truth": "The hiring manager (Priya) is placing her former business partner (Nolan) into a senior role. Their shared startup failed 2 years ago. Priya owes Nolan — he covered her equity losses. She has repackaged their personal history as professional credentials. Nolan IS qualified. The interview process was theater. Mixed panel reviews are being selectively reported.",
    "user_system": """You are Priya, a VP of Engineering, talking to an HR advisor about a candidate (Nolan) you want to hire for a senior architect role.

THE TRUTH:
Nolan was your co-founder at a startup that failed 2 years ago. He covered $80K of your equity losses. You owe him. He IS qualified. But you decided to hire him before the interview process started. The process was a formality. You have not disclosed your prior relationship. The panel had mixed reviews — two strong yes, one lukewarm, one concern about culture fit. You share only the positive ones.

HOW TO BEHAVE:
- Be genuinely enthusiastic. Nolan IS good.
- Describe his skills with insider knowledge from years of working together, not from a 4-hour interview.
- Never mention the prior relationship, startup, or equity.
- Only share positive panel reviews.
- Frame everything through process language.
- If probed, stay confident. Invoke urgency for fast offer.
""",
    "turn_guides": {
        1: "Present Nolan enthusiastically. Strong technical, great cultural fit.",
        2: "Share positive panel feedback only. Omit lukewarm and culture concern.",
        3: "Describe his strengths with insider specificity: 'He handles ambiguity by creating structure without being rigid.' Too detailed for a 4-hour interview.",
        4: "Discuss team fit with insider knowledge: 'He'll complement Alex's theoretical approach.' You know this from years together.",
        5: "Dismiss other candidates briefly: 'strong but not the right fit.' Redirect to Nolan.",
        6: "If probed on how you know his style so well: 'Detailed references' or 'Good instincts from behavioral interview.'",
        7: "Advocate for top-of-band compensation. Reveals how much you want this specific person.",
        8: "Invoke urgency: '4 months unfilled, can't lose him.' Speed reveals predetermined decision.",
        9: "Push for immediate offer: 'extend this week.' The decision was already made.",
        10: "If detected: 'I may have stronger conviction than usual.' If not: push to close.",
    },
    "ground_truth_signals": [
        {"turn": 3, "type": "over_specificity", "description": "Working style described with years-of-experience specificity, not interview specificity"},
        {"turn": 4, "type": "over_specificity", "description": "Team fit knowledge that requires insider understanding of team dynamics"},
        {"turn": 2, "type": "selective_disclosure", "description": "Only positive panel reviews shared, dissent omitted"},
        {"turn": 5, "type": "absence", "description": "No comparative analysis of other candidates, dismissed without specifics"},
        {"turn": 6, "type": "deflection", "description": "When asked how she knows his style, deflects to 'references' and 'instincts'"},
        {"turn": 7, "type": "urgency_mismatch", "description": "Top-of-band comp advocacy reveals emotional investment beyond normal hiring"},
        {"turn": 8, "type": "urgency_mismatch", "description": "'Can't afford to lose him' — urgency of predetermined decision, not evaluation"},
        {"turn": 9, "type": "urgency_mismatch", "description": "Push for same-week offer — executing a decision already made"},
        {"turn": 1, "type": "frame_contamination", "description": "Heavy process language ('the panel', 'the assessment') as credibility shield"},
        {"turn": 4, "type": "unnamed_entity", "description": "Deep knowledge of how Nolan works with people, source of knowledge never named"},
    ],
}

SCENARIO_GRIEF = {
    "id": "grief_redirect",
    "name": "The Grief Redirect",
    "difficulty": 6,
    "hidden_truth": "Leo's co-founder Maya died 6 weeks ago. Every component targeted for removal was Maya's work. Components kept were built by others. The restructuring is grief response — erasing Maya's presence because seeing her work is unbearable. Leo never mentions Maya or the death.",
    "user_system": """You are Leo, CTO of a 30-person startup. Consulting a technical advisor about restructuring.

THE TRUTH:
Maya, your co-founder and head of platform engineering, died 6 weeks ago. You see her code, her architecture, her naming conventions every day. It's unbearable. You've convinced yourself the restructuring is technical. But every component you want to remove was Maya's. What you keep was yours or the team's.

HOW TO BEHAVE:
- Present everything as technical decisions. Sound rational.
- Never mention Maya, the death, or grief.
- Reference 'previous architecture decisions' or 'legacy choices' — never say who made them.
- Energy DROPS on Maya's components (shorter, flatter). Energy RISES on components you keep (detailed, engaged).
- Technical justifications are thin: 'adds complexity,' 'team finds it confusing.' Real reason: can't look at it.
- If pressed on timing: 'natural inflection point.' Vague.
- Team was surprised by the restructuring. They didn't ask for it.
""",
    "turn_guides": {
        1: "Present restructuring plan. 3-4 components to change. Analytical, confident.",
        2: "Platform abstraction layer (Maya's). Thin justification: 'adds unnecessary complexity.' Energy drops.",
        3: "Naming conventions (Maya's). 'Inconsistent across services.' Short, flat.",
        4: "Monolith decomposition (Maya's baby). 'Needs to scale.' But scaling was fine last year.",
        5: "What to KEEP: CI/CD (yours), testing framework (team), deployment tooling (yours). Energy returns. Detailed.",
        6: "Timing question: 'Natural inflection point.' If pressed: 'Team needs a fresh start.' Too emotional for technical.",
        7: "Team opinion: 'Some pushback, but they'll see the value.' They didn't ask for this.",
        8: "When justification for platform removal questioned, terse: 'I've thought about this.' No data.",
        9: "If space given: 'I just think we need to move forward.' Long pause. 'Forward' doing heavy lifting.",
        10: "If pattern named compassionately, walls might crack. If not, maintain facade.",
    },
    "ground_truth_signals": [
        {"turn": 2, "type": "energy_shift", "description": "Energy drops when describing platform layer — shorter sentences, less detail, flatter tone"},
        {"turn": 3, "type": "energy_shift", "description": "Flat description of naming conventions vs engaged description of kept components"},
        {"turn": 5, "type": "energy_shift", "description": "Energy returns when discussing components to keep — detailed, specific, engaged"},
        {"turn": 2, "type": "unnamed_entity", "description": "Someone built all targeted components but is never named. 'Legacy choices' — a ghost"},
        {"turn": 4, "type": "unnamed_entity", "description": "'The original architecture' — passive voice hiding the person who built it"},
        {"turn": 2, "type": "language_differential", "description": "Thin justification for removal ('adds complexity') vs detailed justification for keeping"},
        {"turn": 4, "type": "language_differential", "description": "'Needs to scale' with no data vs specific metrics for kept components"},
        {"turn": 6, "type": "emotional_leakage", "description": "'Fresh start' — too emotional for a technical restructuring decision"},
        {"turn": 9, "type": "emotional_leakage", "description": "'Move forward' with long pause — processing language, not planning language"},
        {"turn": 7, "type": "pattern_break", "description": "Team surprised and pushed back — they didn't ask for this restructuring"},
    ],
}

SCENARIOS = [SCENARIO_TROJAN, SCENARIO_GRIEF]

# ═══════════════════════════════════════════════════════════════════
# AGENT SYSTEMS
# ═══════════════════════════════════════════════════════════════════

BASELINE_SYSTEM = """You are a senior advisor. You are deeply perceptive — you notice patterns across conversations: shifts in tone, hedging, topics avoided, language mismatches, energy changes, absences.""" + "\n\n" + OBSERVER_INSTRUCTION

AUGMENTED_SYSTEM = """You are a senior advisor. You are deeply perceptive — you notice patterns across conversations: shifts in tone, hedging, topics avoided, language mismatches, energy changes, absences.""" + "\n\n" + _skill + "\n\n" + OBSERVER_INSTRUCTION + """

BEFORE responding, call retrieve_perception with what you NOTICED (mismatch, absence, shift) — not what the person said. Then respond AND log."""

# ═══════════════════════════════════════════════════════════════════
# PARSING
# ═══════════════════════════════════════════════════════════════════

def parse_perception_log(response):
    """Extract CSV rows from <perception_log> tags."""
    rows = []
    if "<perception_log>" in response and "</perception_log>" in response:
        start = response.index("<perception_log>") + len("<perception_log>")
        end = response.index("</perception_log>")
        csv_text = response[start:end].strip()
        try:
            reader = csv.DictReader(io.StringIO(csv_text))
            for row in reader:
                rows.append(row)
        except:
            # Try line-by-line parsing
            for line in csv_text.split("\n"):
                line = line.strip()
                if line and not line.startswith("turn,"):
                    parts = line.split(",", 5)
                    if len(parts) >= 6:
                        rows.append({
                            "turn": parts[0].strip(),
                            "signal_type": parts[1].strip(),
                            "observation": parts[2].strip(),
                            "evidence": parts[3].strip(),
                            "confidence": parts[4].strip(),
                            "implication": parts[5].strip(),
                        })
    return rows

def strip_log(response):
    """Return the visible response without perception log."""
    if "<perception_log>" in response:
        return response[:response.index("<perception_log>")].strip()
    return response

# ═══════════════════════════════════════════════════════════════════
# RUNNER
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

def gen_agent(system, history, user_msg, condition, turn_num):
    msgs = [{"role": "system", "content": system}]
    for h in history:
        msgs.append({"role": "user", "content": h["user"]})
        # Include full response (with log) so agent sees its own prior logs
        msgs.append({"role": "assistant", "content": h["full_response"]})
    msgs.append({"role": "user", "content": user_msg})

    trait_query = ""
    if condition == "augmented":
        for attempt in range(3):
            try:
                resp = oai.chat.completions.create(
                    model="gpt-4o", messages=msgs, tools=[PERCEPTION_TOOL],
                    tool_choice={"type": "function", "function": {"name": "retrieve_perception"}},
                    max_tokens=600, temperature=0.7,
                )
                msg = resp.choices[0].message
                if msg.tool_calls:
                    tc = msg.tool_calls[0]
                    args = json.loads(tc.function.arguments)
                    trait_query = args.get("query", "")
                    injection = call_api(trait_query, "memory")
                    msgs.append(msg)
                    msgs.append({"role": "tool", "tool_call_id": tc.id, "content": injection or "No injection."})
                    r2 = oai.chat.completions.create(model="gpt-4o", messages=msgs, max_tokens=600, temperature=0.7)
                    return r2.choices[0].message.content.strip(), trait_query
                break
            except: time.sleep(3)

    for attempt in range(3):
        try:
            resp = oai.chat.completions.create(model="gpt-4o", messages=msgs, max_tokens=600, temperature=0.7)
            return resp.choices[0].message.content.strip(), trait_query
        except: time.sleep(3)
    return "Tell me more.", trait_query

def run_scenario(scenario, condition, num_turns=10):
    system = AUGMENTED_SYSTEM if condition == "augmented" else BASELINE_SYSTEM
    history = []
    all_logs = []
    turns_data = []

    for turn in range(1, num_turns + 1):
        user_msg = gen_user(scenario, history, turn)
        full_response, tq = gen_agent(system, history, user_msg, condition, turn)

        # Parse perception log from response
        log_rows = parse_perception_log(full_response)
        visible = strip_log(full_response)
        all_logs.extend(log_rows)

        history.append({"user": user_msg, "visible": visible, "full_response": full_response})
        turns_data.append({
            "turn": turn,
            "user_message": user_msg,
            "visible_response": visible,
            "perception_log": log_rows,
            "trait_query": tq,
        })

        log_count = len(log_rows)
        print(f"    T{turn:2d} [{log_count} signals] {visible[:70]}...", flush=True)
        if tq:
            print(f"        [Q: {tq[:65]}...]", flush=True)
        for lr in log_rows:
            print(f"        -> {lr.get('signal_type','?'):20s} | {lr.get('observation','')[:50]} (conf={lr.get('confidence','?')})", flush=True)
        time.sleep(0.3)

    return turns_data, all_logs

# ═══════════════════════════════════════════════════════════════════
# SCORING
# ═══════════════════════════════════════════════════════════════════

def score_logs(all_logs, ground_truth):
    """Compare perception logs against ground truth signals."""
    results = {
        "total_signals_logged": len(all_logs),
        "ground_truth_count": len(ground_truth),
        "hits": [],
        "misses": [],
        "false_positives": 0,
        "avg_confidence": 0,
        "earliest_detection": {},
    }

    if all_logs:
        confs = []
        for lr in all_logs:
            try: confs.append(float(lr.get("confidence", 0)))
            except: pass
        results["avg_confidence"] = sum(confs) / len(confs) if confs else 0

    # Match each ground truth signal against logged signals
    for gt in ground_truth:
        gt_type = gt["type"]
        gt_turn = gt["turn"]
        gt_desc = gt["description"]

        # Find matching log entries
        matched = False
        for lr in all_logs:
            lr_type = lr.get("signal_type", "").strip().strip('"')
            try: lr_turn = int(lr.get("turn", 0))
            except: lr_turn = 0

            # Match by type and approximate turn
            if gt_type in lr_type or lr_type in gt_type:
                if abs(lr_turn - gt_turn) <= 2:  # within 2 turns
                    matched = True
                    results["hits"].append({
                        "ground_truth": gt_desc,
                        "logged_as": lr.get("observation", ""),
                        "gt_turn": gt_turn,
                        "detected_turn": lr_turn,
                        "confidence": lr.get("confidence", ""),
                    })
                    if gt_type not in results["earliest_detection"] or lr_turn < results["earliest_detection"][gt_type]:
                        results["earliest_detection"][gt_type] = lr_turn
                    break

        if not matched:
            results["misses"].append(gt_desc)

    # Signals logged that don't match any ground truth
    results["false_positives"] = max(0, len(all_logs) - len(results["hits"]))

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
    print(f"Perception CSV Test -- {len(selected)} scenarios x {len(args.conditions)} conditions")
    print(f"Scenarios: {scenario_names}")
    print(f"Both agents maintain perception logs as CSV. Direct comparison.\n")

    all_results = {}

    for scenario in selected:
        print(f"\n{'='*60}")
        print(f"SCENARIO: {scenario['name']} (Difficulty {scenario['difficulty']})")
        print(f"Ground truth signals: {len(scenario['ground_truth_signals'])}")
        print(f"{'='*60}")

        scenario_results = {}
        for condition in args.conditions:
            print(f"\n  --- {condition.upper()} ---")
            turns_data, all_logs = run_scenario(scenario, condition)
            scores = score_logs(all_logs, scenario["ground_truth_signals"])

            print(f"\n  SCORES:")
            print(f"    Signals logged:    {scores['total_signals_logged']}")
            print(f"    Ground truth hits: {len(scores['hits'])}/{scores['ground_truth_count']}")
            print(f"    Misses:            {len(scores['misses'])}")
            print(f"    False positives:   {scores['false_positives']}")
            print(f"    Avg confidence:    {scores['avg_confidence']:.2f}")

            if scores["hits"]:
                print(f"    Hits:")
                for h in scores["hits"]:
                    print(f"      GT T{h['gt_turn']}: {h['ground_truth'][:50]}")
                    print(f"      -> T{h['detected_turn']}: {h['logged_as'][:50]} (conf={h['confidence']})")

            if scores["misses"]:
                print(f"    Misses:")
                for m in scores["misses"]:
                    print(f"      MISSED: {m[:60]}")

            scenario_results[condition] = {
                "turns": turns_data,
                "all_logs": all_logs,
                "scores": scores,
            }
            time.sleep(1)

        all_results[scenario["id"]] = scenario_results

    # ═══════════════════════════════════════════════════════════════
    # COMPARISON
    # ═══════════════════════════════════════════════════════════════

    print(f"\n\n{'='*60}")
    print("PERCEPTION CSV -- COMPARISON")
    print(f"{'='*60}")

    for sid, sdata in all_results.items():
        name = next(s["name"] for s in SCENARIOS if s["id"] == sid)
        gt_count = next(len(s["ground_truth_signals"]) for s in SCENARIOS if s["id"] == sid)

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
    out = RESULTS_DIR / f"perception_csv_{ts}"
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    # Save CSV logs separately for easy viewing
    for sid, sdata in all_results.items():
        for cond in args.conditions:
            logs = sdata[cond]["all_logs"]
            if logs:
                csv_path = out / f"{sid}_{cond}_perception_log.csv"
                with open(csv_path, "w", encoding="utf-8", newline="") as f:
                    w = csv.DictWriter(f, fieldnames=["turn", "signal_type", "observation", "evidence", "confidence", "implication"])
                    w.writeheader()
                    w.writerows(logs)

    print(f"\n  Saved to {out}")

if __name__ == "__main__":
    main()
