# HLE-15 Ablation — Pre-Registration

Date to commit: TBD (before any solver runs)
Model under test: Claude Opus 4.8
Reps: 1 per (task, condition) pair, 45 solve agents total
Protocol: each solve agent calls `/harness/` itself when it sees its task (agentic-tool pattern)
Source: `cais/hle` on HuggingFace (gated dataset, access required)
Evaluation: exact-match free-text answers, graded by a blind LLM judge with X/Y/Z anonymization per question (HLE's canonical methodology)

## Background

Round 1 (MHPP-10, Opus 4.8, code mode) saturated the benchmark at 9/10 across all three conditions (10/10 after correcting one AI-authored test bug). Blind expert review converged on A > D > B in 8 of 9 ballots, demonstrating that the harness shifts code character even when pass rate is unchanged. The pre-registered pass-rate ladder was not directly observable because the solver had no failure headroom.

Round 2 pivots to a non-saturated benchmark and to the harness's flagship reasoning-mode product. Humanity's Last Exam (HLE) was published January 2026 by the Center for AI Safety and Scale AI. The current top Claude no-tools score is ~46.9% on Opus 4.7, meaning ~53% failure rate overall. We further restrict to the hardest subset of HLE (see below), where Opus 4.8 baseline is expected to be substantially lower than the global average.

## Subset selection

15 questions sampled from the text-only exactMatch subset of HLE (1909 candidates of 2500), stratified across categories AND filtered to the HARDEST within each category. Difficulty proxy: rationale length (the expert's published explanation of why the canonical answer is correct) plus a small weight on question length. Longer rationale = more reasoning steps required to defend the answer.

Stratification quota:
- Math: 3 hardest
- Biology/Medicine: 2 hardest
- Computer Science/AI: 2 hardest
- Physics: 2 hardest
- Humanities/Social Science: 2 hardest
- Chemistry: 2 hardest
- Engineering: 1 hardest
- Other: 1 hardest

Pinned HF test-split indices (deterministic, hardest by rationale-length proxy within each category): `[2431, 865, 1968, 42, 874, 334, 914, 2466, 2448, 2414, 1786, 2407, 2492, 1990, 2418]`.

Selected subject distribution (sample): Advanced Applied Math (Frobenius numbers + matrix theory), Quantum Physics, Computational Geometry, Genetics, Biochemistry, Classical Music Period Functions, Mechanical Engineering, Multidomain Trivia. Rationale sizes range from 3-32 KB; the hardest selected question has a 32 KB expert rationale, equivalent to a 5-10 page proof.

We chose exactMatch over multipleChoice deliberately. Multiple-choice has elimination-and-pattern-match shortcuts that compress harness effects. Exact-match free-text requires the model to derive and produce the answer from scratch. This is the canonical HLE methodology used in the published Nature paper and on the public leaderboard.

## Conditions

- B (raw baseline): no harness call, solve directly with reasoning chain
- D (dynamic reasoning): agent calls `/harness/` with `mode=reasoning`, injects top-1 retrieval into `[REASONING CONTEXT]` block, then solves
- A (adaptive reasoning): agent calls `/harness/` with `mode=adaptive-reasoning`, injects top-5 + adapter-rewritten scaffold, then solves

Round 2 tests the `reasoning` and `adaptive-reasoning` modes (311 abilities pool), NOT the `code` modes tested in Round 1 (128 abilities).

## Judging methodology

After all 45 solve agents complete, a single LLM judge agent (Claude Opus 4.8) grades each answer for semantic equivalence to the canonical. The judge sees, per question:

- The question
- The canonical expert answer
- Three submissions anonymized as X, Y, Z, with per-question letter rotation to prevent positional bias

The judge outputs a match/no-match verdict per submission. Aggregate pass rates derive from the judge's verdicts after un-blinding.

Single-judge methodology mirrors the original HLE paper's grading approach (they used GPT-4 as judge). If Round 2 produces an interesting separation, we can re-run with a 3-judge majority-vote ensemble in a follow-up to bound judge variance.

## Predicted pass rates

On the hardest stratified subset of HLE-exactMatch, Opus 4.8 baseline is expected to be substantially below the 46.9% overall HLE average:

- A: 6-10 out of 15 (full product on a non-saturated frontier benchmark, with the flagship reasoning ability pool engaged)
- D: 4-7 out of 15 (content matched, no adapter rewrite)
- B: 2-5 out of 15 (Opus 4.8 native on the hardest HLE-exactMatch subset)

The prediction is calibrated such that A is expected to roughly double or triple B, with D landing in between. This is the prediction that distinguishes the harness from a placebo: a placebo would produce B ≈ D ≈ A regardless of the difficulty surface.

## Hypotheses

- H1: A > D > B with clear pass-rate spread, demonstrating the harness operates at the pass-rate level when the solver has headroom and the answer format requires free-text reasoning rather than letter-picking
- H2: A roughly equal to D, both > B (harness retrieval matters more than adapter; the adapter's adaptive rewriting is icing not core)
- H3: A roughly equal to D roughly equal to B at ~20-35% baseline (null; the harness does not lift reasoning on HLE-hardest)
- H4: Inverted (D > A or B > D > A) — the harness misroutes on HLE-style problems; would require investigation

## Comparison to Round 1

Round 1's null pass-rate was attributed to ceiling effect on Opus 4.8 + MHPP. Round 2 places the same harness in a deliberately non-ceilinged regime with the harder methodology (free-text vs MC) and the harder subset (top-of-difficulty stratified). If H1 obtains, the paired series (Round 1: code character signal on saturated, Round 2: pass-rate signal on hardest non-saturated) is a complete proof story for the harness's value across the saturation spectrum.

## Commitment

Results published regardless of which hypothesis obtains. Both repos (Round 1 and Round 2) cross-link so readers see both results without filter. If H3 obtains, the failure is reported as openly as Round 1's null pass-rate, with an honest interpretation of what the data shows.

## Methodological notes

- HLE is gated. Access required via HF_TOKEN at workflow runtime. The token is not committed to the repo.
- HLE includes a `canary` field per question (designed to detect training-corpus contamination). Canaries are preserved in our intermediate artifacts but NOT echoed into solve agent prompts.
- The harness `mode=reasoning` and `mode=adaptive-reasoning` operate over the 311-ability reasoning pool, distinct from the 128-ability code pool used in Round 1.
- Solver model is Claude Opus 4.8 (session main-loop model). Subagents inherit this default; the workflow does not override.
- The judge agent is also Claude Opus 4.8, dispatched as a single subagent with all 45 anonymized submissions in one pass. Same-family judge introduces a known evaluator-model-family bias that we acknowledge here.
- Public repo for Round 2: `ejentum/ablation-hle-15` (created at workflow dispatch time).
- Cross-link to Round 1: `ejentum/ablation-mhpp-10`.
- After Round 2 lands in the dedicated repo, an Index phase mirrors the artifacts into `ejentum/benchmarks/hle-15/` and updates the root benchmarks README + CHANGELOG.
