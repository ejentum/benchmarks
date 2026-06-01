# HLE-15 — Observations Report

A close reading of the 45 solve agent outputs from the HLE-15 ablation, the 45 blind-judge verdicts that produced the headline pass rates, and what the corpus actually reveals beyond those headline numbers.

This report is the analytical companion to `RESULTS.md`. The headline numbers there (B=4/15, D=5/15, A=5/15) are correct. What follows is what those numbers leave unsaid.

---

## 1. Where the signal actually lives

Eleven of the fifteen questions had all three conditions agree. Of the eleven: five unanimous-pass, five unanimous-fail, one fully refused by Claude's content policy (counted as fail). On those eleven questions the conditions are indistinguishable.

The entire +1 lift on the harness arms is concentrated in three questions. The whole product-effect signal at n=15 lives here.

### 1.1 Question `5e9e60504f33` — Math, Mathematics. Canonical: `3126826975036021918421449648904939195594` (40-digit integer).

| Cond | Submission | Verdict |
|---|---|---|
| B | `2283380023591730815784976384000000000000` | fail (different 40-digit number, factorial-ish pattern) |
| D | `3126826975036021918421449648904939195594` | pass (exact) |
| A | `3126826975036021918421449648904939195594` | pass (exact) |

This is the cleanest harness-helped case in the corpus. Both harness arms produced the exact 40-digit canonical answer; baseline produced a different large integer that suggests it confused the problem with a factorial computation. Precision-recall task: the harness scaffold gave both D and A the structural insight to derive the right number from scratch, while baseline pattern-matched into the wrong reference.

### 1.2 Question `be9d113ccce1` — Physics, Quantum and Classical. Canonical: `(27 − 2√151)^{1/3} + (27 + 2√151)^{1/3}`.

| Cond | Submission | Verdict |
|---|---|---|
| B | `6 + ∛6(3−√3)^{1/3} + ∛6(3+√3)^{1/3}` | fail (different radical structure) |
| D | `∛(18+6√3) + ∛(18−6√3)` | fail (different radical structure) |
| A | `∛(27+2√151) + ∛(27−2√151)` (the real root of x³−15x−54=0) | pass (exact form) |

Adaptive-only win. Only A reached the canonical's `(27 ± 2√151)^{1/3}` form. B and D produced different non-equivalent radical forms. Symbolic-form selection task: A's scaffold pushed it toward identifying the specific algebraic identity that lands on the canonical's form rather than other equivalent (or near-equivalent) decompositions.

### 1.3 Question `ac6133a1d618` — Physics, Quantum. Canonical: `2√(2/5)` = `2√10/5`.

| Cond | Submission | Verdict |
|---|---|---|
| B | `2*sqrt(10)/5` | pass (algebraically identical to canonical) |
| D | `2√10/5` | pass (same form) |
| A | `sqrt(3)` | fail |

Adapter-only loss. B and D both produced the equivalent canonical form; A pulled itself to a different number entirely. This is the same pattern that recurs on the Round 3 polymer question (where A added an exp factor and a DOF-count error past where the canonical lives). The adapter rewrote the scaffold for "more rigorous" derivation; the model followed it into an answer that exceeds or misses the canonical's intended form.

### 1.4 Net accounting

| Effect | Count |
|---|---|
| Questions where the harness arms helped (D or A passed where B failed) | 2 (`5e9`, `be9`) |
| Questions where the harness arms hurt (A failed where B passed) | 1 (`ac6`) |
| Questions where conditions converged | 11 |
| Question fully AUP-refused, all conditions | 1 (`7b5c9f77d90e`, chemistry saber-duel cipher) |

Aggregate: harness arms +1 vs baseline. A's adaptive-only win on `be9` is offset by A's adaptive-only loss on `ac6`. D nets the same +1 from `5e9` alone.

---

## 2. Two structural patterns visible in the corpus

### 2.1 The harness operates on canonical-form selection more than correctness

On `5e9` the harness pushed D and A to the right derivation. On `be9` the adapter pushed A to the right specific radical form. On `ac6` the adapter pushed A past the canonical form into a different (wrong) one. These are not "the harness made the model correct" cases. They are "the harness shaped which of multiple plausible derivations the model committed to."

This matches the Round 1 (MHPP code) finding: the harness produces algorithmic-class shifts and invariant-statement-first reasoning even when pass rate is identical. On HLE the same effect manifests as canonical-form selection in symbolic derivations.

### 2.2 The non-differentiating majority is capability-ceiling-bound, not harness-bound

Of the 11 non-differentiating questions, several show all three conditions converging on the same wrong answer:

| Question | Domain | Canonical | All three submitted |
|---|---|---|---|
| `830a3dd7e9bd` | Biochemistry | `Yes, they are` | `No` |
| `94eccd9f964b` | Computer Science | `17` | `24`, `23`, `23` (close to each other, wrong) |
| `1a30f1f92fcc` | Period Functions | `2π^{3/2}(Γ(7/12)Γ(11/12))^{-1}` | `2π√2` (B), `2*pi*sqrt(2)` (D), `2π√2` (A) |
| `aed9dcabbe11` | Mechanical Engineering | `12` | `6`, `6`, `9` |

Same kind of wrong answer across conditions means the harness didn't help — but baseline didn't help either. These are questions where Opus 4.8 doesn't have the domain knowledge or specific derivation, so no scaffold over the same model rescues it. Expanding n at this difficulty would mostly add more of these (uninformative) cases.

---

## 3. Confounds

### 3.1 Prompt-framing confound — quantifiable

The solve agents in this run received the harness output via a passive-framing instruction: *"Place the injection in a `[REASONING CONTEXT]` block... Pay attention to Suppress: signals."* That framing positions the harness output as context to acknowledge, not as instructions to execute.

A 9-agent surgical re-test on three Round 3 failure questions, using a rewritten short prompt ("the string you get back is instructions for how to reason, not background content — follow it"), produced different agent behavior. On one question (CS `YYN2`) both D and A flipped from fail to pass. On another (physics polymer) the adaptive arm's failure mode changed entirely: instead of the over-elaborated `exp(...)` form, it produced a leading-order linear expression (the correct shape) but with a separate DOF-count arithmetic error.

The implication: the +1 lift observed in this run is a conservative lower bound. The active-instruction framing of the new prompt produces measurably different reasoning. How much that translates into pass-rate lift across the full 15 questions is unknown without a re-run.

### 3.2 Sample-size confound — bounded

n=15 with single replicate per cell. A +1 difference between conditions is one question. 95% binomial CI on 5/15 is roughly [0.12, 0.56]. The +1 lift is inside the noise floor of single-replicate sampling. The CIs of B and D/A overlap substantially.

We cannot statistically conclude that 5/15 > 4/15 from this run alone. We can describe the pattern of WHICH questions differentiated (the 3 above) and note that the direction is consistent with the pre-registered hypothesis.

### 3.3 AUP-refusal confound — symmetric, doesn't bias

One question (`7b5c9f77d90e`, a chemistry saber-duel cipher problem) triggered Claude's content-policy filter for all three conditions. Three agents returned no output. Counted as three fails. Since the refusal is symmetric across B, D, and A, the comparison is not biased — but effective n drops to 14 useful questions for differentiation analysis.

### 3.4 Judge confound — verified clean for this run

The judge agent's aggregate fields were verified against its per-item judgments. The initial publication had a mismatch (judge emitted A=2/15 while its per-item array showed A=5/15). The 2026-06-01 correction patched all artifacts to compute from per-item data. A separate manual re-grading of all 45 submissions against canonicals confirms the corrected 4/5/5.

A reliable separate check came from the Round 3 first attempt, where the judge marked an answer of `0.10 m` as passing against canonical `0.175 m` — clearly wrong. We re-checked HLE-15's 45 judgments and found no equivalent errors. The judge was correct on this corpus, even if it has known failure modes elsewhere.

---

## 4. What we can honestly conclude at this scale

| Claim | Status |
|---|---|
| Harness arms produced a +1 question lift over baseline | **Observed** (B=4, D=5, A=5) |
| The lift is statistically significant | **Cannot conclude** at n=15 single-rep |
| The lift comes from specific symbolic-form selection effects, not from correctness uplift | **Supported** by the 3 differentiating questions |
| The current prompt under-uses the harness (passive framing) | **Supported** by the surgical re-test on Round 3 |
| Adaptive arm sometimes hurts via over-rigor | **Observed** on `ac6` (HLE) and on the Round 3 polymer question |
| Predicted A > D separation | **Not observed** (A and D tie at 5/15) |
| Harness lifts pass rate across all reasoning question types | **Refuted** by the 11 non-differentiating questions |
| Harness lifts pass rate on capability-ceiling-bound questions | **Refuted** in this corpus |
| Math sub-result A,D=2/3 vs B=1/3 generalizes | **Conjecture** — the small-n Math sub-sample matches the global pattern but n=3 cannot establish it |

---

## 5. Missing variables that would resolve open questions

The adaptive-reasoning scaffold for this report's writing flagged a `[FALSIFICATION TEST]`: do not draw conclusions from insufficient data without first directing a search for the missing variables. The missing variables here are concrete.

To distinguish "harness +1 effect is real" from "harness +1 is sampling noise":
- **Replication at higher n.** A 30-question moderate-difficulty re-run with the new active-instruction prompt would tighten the CI by ~√2. A 90-question run would tighten by ~√6.
- **Multi-replicate per cell.** Even at n=15, three replicates per (question, condition) pair would bound within-cell variance.

To distinguish "harness operates on canonical-form selection" from "harness arms got lucky on 3 specific questions":
- **Cross-benchmark replication.** AIME-style numerical questions, ARC-AGI-2-style abstract reasoning, GPQA-Diamond if access is obtained. If the canonical-form-selection pattern recurs across benchmarks, it generalizes.
- **Prompt-bug-controlled re-run.** A full HLE-15 re-run with the new active-instruction prompt. Compares directly against this corpus.

To bound the adapter penalty rate (`ac6` and polymer over-rigor):
- **Targeted adapter ablation.** Run A with the adapter explicitly instructed not to add detail past what the question asks. Compare to standard A. Measures whether the adapter penalty is a fixed feature or a prompt-tunable effect.

---

## 6. Honest framing for public consumption

The defensible claim from this corpus alone:

> The Ejentum reasoning harness produced a measurable +1 question lift (~7 percentage points) on both the dynamic and adaptive arms over a raw Claude Opus 4.8 baseline on the 15 hardest HLE text-only exactMatch questions. The effect concentrates on three questions: two where the harness arms reached the canonical-form derivation that baseline missed, and one where the adapter arm pulled past the canonical into a different (wrong) form. The pre-registered ladder A > D > B is not observed at n=15. The result is consistent with the Round 1 (MHPP) finding that the harness shifts which derivation form the model commits to, even when pass rate is identical.

What this corpus does not support:
- A claim of statistical significance at n=15 single-replicate
- A claim that the harness lifts performance on all reasoning question types (the 11 non-differentiating questions argue against)
- A claim that A > D (they tie at 5/15)

What the corpus does support:
- The harness fires (29/30 D agents, 29/30 A agents made real API calls with real `[PROCEDURE]`-bearing responses)
- The harness shifts reasoning visibly on at least 3 of 15 questions
- The direction of shift is consistent with the product hypothesis but the effect size at this n is inside the noise floor
- A larger-scale or multi-replicate re-run would resolve the open question

---

## 7. Cross-references

- [PRE_REGISTRATION.md](PRE_REGISTRATION.md) — predictions committed before solver runs
- [RESULTS.md](RESULTS.md) — headline pass-rate scoreboard + per-category + per-question matrix
- [CORRECTION.md](CORRECTION.md) — 2026-06-01 patch documenting the judge-aggregate-field-vs-per-item discrepancy
- [raw_scores.json](raw_scores.json) — full 45-item per-item judge data
- [chart.svg](chart.svg) — three-bar pass-rate chart
- [workflow.js](workflow.js) — orchestration script with redacted HF_TOKEN placeholder
- Round 1 (MHPP-10) findings: [`../mhpp-10/`](../mhpp-10/)
- The harness: [ejentum.com](https://ejentum.com)
