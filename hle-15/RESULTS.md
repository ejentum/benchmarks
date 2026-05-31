# HLE-15 Ablation — Results

**[CORRECTED 2026-06-01.](CORRECTION.md)** The initial RESULTS.md published with this run reported `A = 2/15`. That number was an arithmetic error in the judge agent's aggregate field; the judge's own 45 per-item judgments produce `A = 5/15`. The numbers below are computed directly from the per-item data in `raw_scores.json` and are correct. See `CORRECTION.md` for the discrepancy detail.

## Headline

| Condition | Pass rate |
|---|---|
| B (raw baseline) | **4 / 15** |
| D (dynamic reasoning, harness `mode=reasoning`) | **5 / 15** |
| A (adaptive reasoning, harness `mode=adaptive-reasoning`) | **5 / 15** |

Both harness arms produced a +1 question lift over raw baseline on this 15-question stratified-hardest subset of Humanity's Last Exam. The pre-registered A > D > B ladder was not observed; instead the result matches H2 from the pre-registration: A ≈ D, both > B.

## Pre-registered prediction vs actual

The pre-registration was committed at SHA `e45aeac5` BEFORE any solver ran.

| Condition | Predicted | Actual |
|---|---|---|
| A | 6-10 / 15 | 5 / 15 |
| D | 4-7 / 15 | 5 / 15 |
| B | 2-5 / 15 | 4 / 15 |

D landed inside the predicted band. A was one below the predicted band. B was at the upper end of its predicted band. The headline ladder pattern (harness > baseline) holds; the predicted A > D separation does not.

## Per-category breakdown

| Category | B | D | A |
|---|---|---|---|
| Math | 1/3 | 2/3 | 2/3 |
| Biology/Medicine | 1/2 | 1/2 | 1/2 |
| Computer Science/AI | 1/2 | 1/2 | 1/2 |
| Physics | 1/2 | 1/2 | 1/2 |
| Humanities/Social Science | 0/2 | 0/2 | 0/2 |
| Chemistry | 0/2 | 0/2 | 0/2 |
| Engineering | 0/1 | 0/1 | 0/1 |
| Other | 0/1 | 0/1 | 0/1 |
| **Total** | **4/15** | **5/15** | **5/15** |

The +1 lift on both harness arms comes entirely from one Math question (`5e9e60504f33`, large-integer answer) where D and A produced the exact canonical answer and B did not.

Several categories show 0 across all conditions: Humanities/Social Science (2 questions), Chemistry (2), Engineering (1), Other (1). These are on the absolute-tail end of HLE difficulty. We selected the hardest-by-rationale-length question within each category, which biases the subset toward problems beyond Opus 4.8's capability ceiling regardless of scaffolding. The Math category was sampled with 3 questions and shows the clearest signal.

## Per-question pass matrix

```
hle_id        category                       B/D/A
1c54a42874ef  Math / Advanced Applied Math   . . .   (Frobenius, 32KB rationale)
5e9e60504f33  Math / Mathematics             . Y Y   ← D+A pass, B fails
32f504545aae  Math / Mathematics             Y Y Y
516dd6ab54da  Biology/Medicine / Genetics    Y Y Y
830a3dd7e9bd  Biology/Medicine / Biochemistry. . .
59a842b73398  CS/AI / Computational Geometry Y Y Y
94eccd9f964b  CS/AI / Computer Science       . . .
be9d113ccce1  Physics / Quantum+Classical    . . Y   ← only A passes
ac6133a1d618  Physics / Quantum Physics      Y Y .   ← only A fails
1a30f1f92fcc  Humanities / Period Functions  . . .
cc48e8cbb7fd  Humanities / History           . . .
7b5c9f77d90e  Chemistry / Saber-duel cipher  . . .   ← AUP refusal, all 3
03ffe2253dd4  Chemistry                      . . .
aed9dcabbe11  Engineering / Mechanical       . . .
08d75b31f329  Other / Multidomain Trivia     . . .
```

## Confounds and threats to validity

This is a small pilot. The result is suggestive, not conclusive.

1. **n=15 with single replicate per cell** (45 solve agents total). The difference between A=5 and A=4 or A=6 is one question. 95% binomial CI on 5/15 is [0.12, 0.56]. The +1 lift over baseline is within the range that single-replicate sampling noise could produce.

2. **Subset is extreme-tail by design.** We picked the hardest question per category by rationale-length proxy. Five of eight categories show 0/0/0 across all conditions, meaning the subset includes questions beyond Opus 4.8's capability ceiling where no scaffolding can lift performance. A moderate-difficulty HLE pilot (e.g., median-rationale-length per category) might show different separation patterns.

3. **AUP refusal on one Chemistry question.** Three agents (the `7b5c9f77d90e` saber-duel cipher question across all three conditions) were refused by Claude's Usage Policy filter. They are counted as fails in the aggregate. Since the refusal is symmetric across conditions, it doesn't bias the comparison but it does reduce effective N by one question for all conditions.

4. **Single-judge methodology.** A single Opus 4.8 judge agent graded all 45 submissions for semantic equivalence with X/Y/Z anonymization rotated per question. This mirrors the original HLE paper's grading approach (they used GPT-4 as judge). A 3-judge majority-vote ensemble would bound judge variance.

5. **The Math category drives the entire aggregate signal.** D and A's +1 over B is one specific Math question. A larger Math-focused pilot would test whether this generalizes.

## Comparison to Round 1

Round 1 (MHPP-10, Opus 4.8, code mode) saturated at 9/10 / 10/10-corrected across all three conditions. The code-character signal was visible in blind expert review even though pass rate was unchanged.

Round 2 (HLE-15, Opus 4.8, reasoning mode) shows a mild pass-rate lift on both harness arms over baseline (+1 question = ~7 percentage points). The pre-registered A > D separation does not appear in this run; A and D tie at 5/15.

The two-round pattern is:
- **Saturated benchmark + code mode:** harness operates on code character. Pass rate is uniform.
- **Non-saturated benchmark + reasoning mode:** harness produces a mild pass-rate lift over baseline. Adapter contribution is not visible at n=15.

## Cross-references

- Pre-registration committed before run: [PRE_REGISTRATION.md](PRE_REGISTRATION.md)
- The harness: https://ejentum.com
- Round 1 (MHPP-10): https://github.com/ejentum/ablation-mhpp-10
- Benchmarks index: https://github.com/ejentum/benchmarks/tree/main/hle-15

## Honest interpretation

This is the pattern the data supports:

The harness produces a measurable pass-rate lift on a non-saturated reasoning benchmark, but the lift is modest (+7 percentage points, single replicate) and the adapter ablation (A vs D) shows no separation in this run. The Math sub-result aligns with the predicted A,D > B pattern. The extreme-tail selection means most non-Math questions are beyond Opus 4.8's capability ceiling regardless of scaffolding, which compresses any separation that might exist on moderate-difficulty problems.

The next experiment is a moderate-difficulty HLE pilot (median-rationale-length per category, n=20-30), or a math-focused pilot like AIME 2025 where the model has fighting chance on most questions.
