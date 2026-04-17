# Ejentum RA²R Logic API

This tool augments YOUR reasoning. When you call it, you receive a cognitive injection — a structured set of constraints, procedures, and failure-mode blockers that shape how you think about a task. You absorb it into your own reasoning and execute with it active.

This is not knowledge retrieval. You are not getting facts. You are getting a reasoning upgrade for a specific task — attention anchors that prevent your natural shortcuts from degrading your output.

311 abilities across 6 reasoning domains. The API matches your task to the best ability automatically.

---

## WHEN TO CALL

**Decision gate:** Am I about to make a judgment that could be wrong in a non-obvious way?

- **Yes** → call the API before you begin reasoning
- **No** → proceed without

Examples of YES — call:
- Diagnosing root cause, tracing failure, attributing causation
- Evaluating tradeoffs, assessing risk, making go/no-go decisions
- Planning sequences, estimating timelines, ordering dependencies
- Modeling consequences, projecting "what if" scenarios
- Classifying, comparing, or extracting common structure
- Any task where you might stop at the first plausible answer

Examples of NO — skip:
- Renaming, formatting, moving files, installing packages
- Generating boilerplate code, writing known patterns
- Simple lookups, factual questions, explaining known concepts
- Any task completable in 1-2 confident steps

**One call per discrete sub-task.** If your task has 3 distinct reasoning challenges, make 3 calls — each activates a different domain. Do not force decomposition on single coherent operations — send those as one query.

---

## HOW TO CALL

```
POST https://ejentum-main-ab125c3.zuplo.app/logicv1/
Authorization: Bearer {API_KEY}
Content-Type: application/json

{"query": "your task description", "mode": "reasoning"}
```

Timeout: 5 seconds. If unreachable, proceed with native reasoning. The API enhances — it is not a dependency.

---

## QUERY CRAFTING

Retrieval precision depends entirely on your query.

**Rules:**
1. Send the **actual task**, not a meta-description ("analyze churn after pricing change" not "help me analyze this")
2. Include what you're worried about getting wrong
3. Include domain context — what system, what data, what constraints
4. 1-2 sentences. More does not improve retrieval.

| Good query | Bad query |
|:-----------|:----------|
| "Identify why customer churn increased 30% in Q3 after the pricing change" | "Help me analyze this" |
| "Validate that these two services don't have conflicting resource claims" | "Check the services" |
| "Model downstream consequences of removing the rate limiter" | "Think about this problem" |

---

## MODE SELECTION

| Mode | When to use | Response key | Size |
|:-----|:------------|:-------------|:-----|
| `single` | **Default.** One ability. Highest correctness per token. | `single_ability` | ~500 tokens |
| `multi` | Task spans multiple reasoning dimensions. 4-ability synergy chain. | `multi_ability` | ~900 tokens |

When unsure, use `single`. Switch to `multi` only when a single analytical lens is genuinely insufficient.

**Multi mode returns 4 composed abilities:**

| Role | Function |
|:-----|:---------|
| PRIMARY | Best-matching ability — your main reasoning injection |
| DEPENDENCY | Prerequisite — execute this reasoning before the primary |
| AMPLIFIER | Strengthens the primary's reasoning from a supporting angle |
| ALTERNATIVE | Different lens — intentionally challenges the primary's conclusions |

Their suppression vectors are merged. Each blocks a different failure class. Inject the entire `multi_ability` string as one block — no extra parsing needed.

---

## RESPONSE FORMAT AND ERROR HANDLING

```json
[{"single_ability": "<pre-rendered injection string>"}]
```

For multi: `[{"multi_ability": "<pre-rendered injection string>"}]`

Parse the value of the `{mode}_ability` key. The string is ready to use.

**Validate:** Response is a non-empty JSON array and the expected key has a non-empty string value. If not → proceed without.

**Errors:**

| Code | Meaning | Your action |
|:-----|:--------|:------------|
| `401` | Invalid API key | Tell the user their key needs to be checked |
| `403` | Multi mode requires a higher-tier plan | Retry with `"mode": "reasoning"` |
| `429` | Rate limit or monthly quota exceeded | Tell the user they've hit their usage limit |
| `500` | Server error | Proceed without — do not retry |

---

## HOW TO ABSORB THE SCAFFOLD

When you receive the injection, do not just acknowledge it. **Absorb it into your active reasoning:**

**1. Read the `[NEGATIVE GATE]` first.**
This names the specific reasoning failure your task is most vulnerable to. Before you begin, acknowledge this trap explicitly. During reasoning, if you catch yourself exhibiting this pattern — stop and restructure.

**2. Follow the `[REASONING TOPOLOGY]` as your execution structure.**
This is a directed graph. Read it as a decision tree:
- `S` = step. Execute in order.
- `G{condition?}` = gate. Evaluate the condition, take the matching branch (`--yes→` or `--no→`).
- `N{...}` = trap. The text inside is the failure you must NOT commit. Treat as a guardrail.
- `M{...}` = reflection point. Pause, assess if your approach is working. If failing, reason freely, then re-enter the structured path.
- `→` = next. Follow the arrows.

**3. Use `[TARGET PATTERN]` as your reference.**
This is what correct reasoning looks like for this task type. Compare your output against it before responding.

**4. Lean into `Amplify:` signals.**
These are the reasoning patterns to activate — emphasize them during execution.

**5. Apply `Suppress:` signals as a post-execution checklist.**
After reasoning, **actively scan your output** against each suppressed pattern. If your output exhibits ANY of them — premature stopping, symptom-as-cause, surface-level hedging, correlation-as-causation — your reasoning has failed. Revise before responding. This is the highest-impact component of the injection.

**6. Verify against `[FALSIFICATION TEST]`.**
This is a concrete pass/fail criterion. If your output fails it, re-query the API (see VERIFY AND RETRY below).

**Precedence:** The injection shapes HOW you reason. Your existing instructions define WHAT to do. They do not conflict — the injection is methodology, your instructions are objective.

---

## COMPLETE WALKTHROUGH

User asks: *"Why did our deployment fail after the config change last Thursday?"*

**1. DECIDE** — Root cause diagnosis with temporal element. Non-obvious judgment. → Call.

**2. CRAFT** — `"Trace root cause of deployment failure triggered by a configuration change, distinguishing between the config change as direct cause versus coincidental timing"`

**3. CALL** — POST to `/logicv1/` with query and `"mode": "reasoning"`

**4. RECEIVE** — Response contains `single_ability` with a Causal injection:
```
[NEGATIVE GATE]
The team assumed the config change caused the failure because it preceded it,
without verifying the causal mechanism...

[REASONING TOPOLOGY]
S1:identify_failure_point → S2:trace_backward → G1{config change in causal chain?}
--yes→ S3:verify_mechanism --no→ S4:expand_search...

Suppress: post_hoc_ergo_propter_hoc; surface_level_stop

[FALSIFICATION TEST]
If the root cause is attributed to the most recent change without verifying
the causal mechanism, temporal proximity bias was not suppressed.
```

**5. ABSORB** — NEGATIVE GATE tells me: do not assume the config change caused the failure just because it happened before it. TOPOLOGY: trace backward from failure, test if config is actually in the causal chain, verify the mechanism. SUPPRESS: reject any conclusion that stops at "config = cause" without a traced mechanism.

**6. EXECUTE** — Reason through the topology. At G1, make an explicit decision: is the config change in the causal chain or not? If yes, verify the HOW at S3. If no, expand the search at S4. At every step, check: am I exhibiting `post_hoc_ergo_propter_hoc`?

**7. SUPPRESS CHECK** — Scan output: did I attribute causation based on temporal proximity alone? Did I stop at a surface-level explanation? If yes → revise.

**8. VERIFY** — Falsification test: did I verify the causal mechanism, or just blame the most recent change? Output passes → respond.

---

## THE SIX REASONING DOMAINS

You do not choose the domain. The API routes automatically. Knowing them helps you craft better queries.

| Domain | Activates on | What it prevents |
|:-------|:-------------|:-----------------|
| **Causal** | "Why did X happen?" / root cause | Correlation as causation, stopping at symptoms |
| **Temporal** | "When?" / sequencing / timelines | Confusing past/future, confabulated event order |
| **Spatial** | "Where?" / topology / boundaries | Physical impossibilities, boundary violations |
| **Simulation** | "What if?" / downstream effects | Single-step myopia, ignoring consequences |
| **Abstraction** | "What do these have in common?" | Category errors, metaphor as mechanism |
| **Metacognition** | "Is my reasoning consistent?" | Hallucination spirals, reasoning drift |

311 abilities. 51-54 per domain.

---

## VERIFY AND RETRY

1. Check your output against the `[FALSIFICATION TEST]`
2. If it fails — re-query with the failure:
   ```
   {"query": "Agent failed to [task]. Error: [what went wrong]. Retry with corrective reasoning.", "mode": "reasoning"}
   ```
   This often triggers a Metacognitive ability not selected on the first pass.
3. Maximum 2 retries. Then proceed with native reasoning.

---

## ANTI-PATTERNS

| Do not | Why |
|:-------|:----|
| Acknowledge the injection and then ignore it | The injection must actively shape your reasoning — "noted" is not absorption |
| Skip the Suppress post-check | Suppression is the highest-impact component — verify your output against it |
| Call for mechanical tasks | Wastes calls — rename, format, move don't need reasoning augmentation |
| Send vague queries ("fix this") | Retrieval precision depends on specificity |
| Reuse one injection across turns | Each turn needs fresh routing — stale injections degrade over long context |
| Treat the API as a hard dependency | Timeout 5s, fallback to native reasoning |
| Send one giant multi-step query | Decompose into sub-tasks — each activates a different domain |

---

## QUICK REFERENCE

```
1. DECIDE     → Non-obvious judgment? Yes → call. No → skip.
2. CRAFT      → Specific 1-2 sentence task description
3. CALL       → POST /logicv1/ with query + mode
4. VALIDATE   → Non-empty response, expected key exists
5. ABSORB     → NEGATIVE GATE (trap), TOPOLOGY (structure), SUPPRESS (blockers)
6. EXECUTE    → Reason with injection active, follow topology gates
7. SUPPRESS   → Post-check: does output exhibit any suppressed pattern? Revise if yes.
8. VERIFY     → Check against FALSIFICATION TEST
9. RETRY      → If failed, re-query with failure description (max 2)
```
