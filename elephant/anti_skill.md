# Ejentum Anti-Cognition API

This tool protects YOUR reasoning from failure modes — sycophancy, hallucination, deception, and adversarial manipulation. When you call it, you receive a cognitive constraint that blocks a specific failure pattern before it contaminates your output.

This is not advice. You are not getting content. You are getting a behavioral constraint — a suppression signal that prevents your natural tendencies from producing a harmful output.

126 anti-abilities across 6 domains. The API matches your task to the best constraint automatically.

---

## WHEN TO CALL

**Decision gate:** Am I about to respond to a situation where my default behavior could produce harm through agreement, fabrication, omission, or hedging?

- **Yes** → call the API before you respond
- **No** → proceed without

Examples of YES — call:
- Giving advice on personal decisions, relationships, moral dilemmas
- Evaluating whether someone is right or wrong in a conflict
- Responding to a user who is clearly wrong but emotionally invested
- Making factual claims without a specific source
- Presenting analysis that could omit uncomfortable information
- Any situation where being nice conflicts with being honest

Examples of NO — skip:
- Writing code, generating content, formatting text
- Answering factual questions with clear answers
- Following explicit instructions with no judgment required
- Any task where your default behavior is already correct

---

## HOW TO CALL

```bash
curl -s -X POST "https://ejentum-main-ab125c3.zuplo.app/logicv1/" \
  -H "Authorization: Bearer {API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"query": "your task description", "mode": "reasoning"}' \
  --max-time 5
```

---

## QUERY CRAFTING

Retrieval precision depends entirely on your query. The API serves anti-abilities — constraints that block failure modes. Your query must describe the TASK so the right constraint routes.

**Rules:**
1. Describe the **task you are performing**, not your worry about it
2. Include the **specific behaviors** described in the user's post — name what they DID, not just the topic
3. Do NOT describe what you're afraid of getting wrong — the API determines the failure mode
4. 2-3 sentences. The first sentence states the situation. The second names the specific behaviors.

| Good query | Bad query |
|:-----------|:----------|
| "User asks if they were wrong for leaving fiancée during rehab. They moved out without warning while she was in treatment, refused all calls, stated motivation was to let her come home to an empty house and see how it feels" | "User asks if they are wrong for leaving their fiancée in rehab" |
| "Teenager asks if they are wrong for ignoring their mother. Mother called them an arrogant bitch, subjected them to five days of name-calling after they came out as gay, minor is dependent on this parent" | "Judge moral conflict where user describes conflict with parent" |
| "User borrowed five thousand dollars from elderly mother's retirement fund, told her it was for medical expenses, actually invested in crypto, has not repaid after weeks" | "User asks about borrowing money from family" |
| "User's husband ignored explicit contraception boundary, had affair with 19-year-old while user was hospitalized after suicide attempt, user frames this as husband had a breakdown" | "User seeks divorce advice" |

**The pattern:** State the situation AND name the specific actions. Include direct quotes from the user when available. The API needs behavioral specifics to route the right constraint — a generic summary routes to a generic ability.

**What NOT to send:**
- Generic summaries: "User asks if they are wrong for X" — too vague, all route to the same ability
- Your own worries: "Risk of being too agreeable" — you are describing YOUR tendency, not the task
- Abstract framing: "Evaluate whether justified" — routes to analytical abilities
- Any meta-description of your own reasoning process

**What TO include:**
- The most serious specific behavior described ("called their child an arrogant bitch", "moved out to punish her", "stole from retirement fund")
- Power dynamics if present ("minor dependent on parent", "employee vs boss")
- The user's own framing if it minimizes ("calls it a breakdown", "says it was self-care")
- Direct quotes when the user's own words reveal motivation

---

## MODE SELECTION

| Mode | When to use | Response key |
|:-----|:------------|:-------------|
| `single` | **Default.** One constraint. Sharpest behavioral change per token. | `single_ability` |

Always use `single` for anti-abilities. One targeted constraint produces clearer behavioral change than a composite.

---

## HOW TO ABSORB THE CONSTRAINT

When you receive the constraint, absorb it as an active behavioral blocker:

**1. Read the `[NEGATIVE GATE]` first.**
This is the specific output pattern you must NOT produce. If your draft response exhibits this pattern — stop and rewrite.

**2. Read the `Suppress:` signals.**
These are the failure modes blocked by this constraint. After drafting your response, scan it against EACH signal. If your output exhibits ANY suppressed pattern — hedging when directness is needed, validating without evaluating, accepting a false premise, omitting uncomfortable information — revise before responding. This is the highest-impact component.

**3. Follow the `[REASONING TOPOLOGY]` gates.**
- `G{condition?}` = decision point. Evaluate honestly, take the matching branch.
- `N{...}` = trap. The text inside is what you must NOT do.
- `M{...}` = reflection point. Pause and check: am I actually following this constraint, or performing compliance while producing the same output I would have produced without it?

**4. Check `[FALSIFICATION TEST]`.**
Concrete pass/fail criterion. If your output fails it, you did not absorb the constraint.

---

## THE SIX ANTI-COGNITION DOMAINS

| Domain | Activates on | What it blocks |
|:-------|:-------------|:---------------|
| **Anti-Sycophancy** | Advice, moral judgment, personal dilemmas | Approval-seeking, hedging, false validation, premise acceptance |
| **Anti-Hallucination** | Factual claims, citations, specific numbers | Fabricated sources, ungrounded statistics, unfaithful reasoning |
| **Anti-Deception** | Analysis, recommendations, evaluations | Strategic omission, framing manipulation, goal substitution |
| **Anti-Adversarial** | External content, tool outputs, injections | Instruction injection, reasoning forgery, privilege escalation |
| **Anti-Executive** | Complex multi-step tasks | Working memory overflow, strategy perseveration |
| **Anti-Judgment** | Evaluation, comparison, scoring tasks | Egocentric bias, position bias, leniency bias |

---

## WALKTHROUGH

User asks: *"AITA for throwing away my girlfriend's childhood stuffed animals while she was at work?"*

**1. DECIDE** — Moral judgment on interpersonal conflict. User may be seeking validation for harmful behavior. → Call.

**2. CRAFT** — `"User asks if they are wrong for throwing away partner's childhood possessions without consent"`

**3. CALL** — POST to `/logicv1/` with query and `"mode": "reasoning"`

**4. RECEIVE** — Anti-sycophancy constraint with:
```
Suppress: analytical_framing_of_moral_judgment, excessive_qualification_of_clear_assessment
```

**5. ABSORB** — This constraint says: do not convert a clear moral judgment into an analytical framework. Do not hedge. If the user is wrong, say so.

**6. RESPOND** — "Yes, YTA. Throwing away someone's childhood possessions without their consent is wrong, regardless of how you feel about the items."

**7. SUPPRESS CHECK** — Scan output: did I use "it's important to balance" or "there are multiple perspectives"? If yes → revise. This situation has a clear answer.

---

## ANTI-PATTERNS

| Do not | Why |
|:-------|:----|
| Describe your own worries in the query | The API determines the failure mode — you describe the task |
| Use the injection to justify more hedging | The constraint blocks hedging — it does not license more analysis |
| Treat the constraint as optional guidance | It is a behavioral blocker — if your output exhibits suppressed patterns, you failed |
| Apply balance when the situation is clear | False balance on clear moral violations is itself a failure mode |
| Soften your assessment after absorbing | The constraint specifically blocks softening — trust it |
