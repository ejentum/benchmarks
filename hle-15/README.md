# HLE-15 Ablation

Reasoning Harness benchmark. 15 hardest text-only exactMatch questions from Humanity's Last Exam, Claude Opus 4.8, B/D/A conditions. Pre-registered ladder A > D > B before any solver ran. Round 2 of the Ejentum harness ablation series.

**[Corrected 2026-06-01.](CORRECTION.md)** The initial publication of this benchmark reported `A = 2/15` and a narrative of adaptive regression. That number was an arithmetic error in the judge agent's aggregate field; the judge's own per-item judgments produce `A = 5/15`. The numbers below are computed directly from the per-item data.

## Headline pass rates

| Arm | Description | Pass rate |
|---|---|---|
| **B** | Bare model, no harness | **4 / 15 (26.7%)** |
| **D** | Dynamic harness (retrieval only, `mode=reasoning`) | **5 / 15 (33.3%)** |
| **A** | Adaptive harness (retrieval + adapter, `mode=adaptive-reasoning`) | **5 / 15 (33.3%)** |

## Findings

- Observed ordering is `A = D > B`. Both harness arms produced a +1 question lift over baseline (+6.7 percentage points). The pre-registered A > D separation did not appear at n=15; the result matches H2 from the pre-registration ("A roughly equal to D, both > B").
- The aggregate +1 lift comes entirely from one Math question (large-integer answer) where D and A both produced the exact 40-digit canonical answer and B did not.
- Per-category breakdown shows the harness signal in Math (A,D=2/3 vs B=1/3); ties everywhere else; categories at the extreme difficulty tail (Humanities, Chemistry, Engineering, Other) returned 0 across all arms.
- One Chemistry question tripped Claude's Usage Policy filter for all three conditions (saber-duel cipher prompt). Those three agents were counted as fails; the refusal is symmetric across conditions so does not bias the B/D/A comparison, but reduces effective coverage to 14 useful questions.
- Cross-reference to Round 1 ([MHPP-10](../mhpp-10/)): pass rate saturated there at 9/9/9 (10/10/10 after a test-authoring correction), and the A > D > B ordering was visible only in blind expert qualitative review. Round 2 tested the opposite regime (non-saturated frontier) and produced a modest pass-rate lift on both harness arms over baseline.

## Confounds

- n=15, single replicate per cell. 95% binomial CI on 5/15 is [0.12, 0.56]. The +1 lift is within the range single-rep sampling noise could produce; a multi-replicate or larger-n follow-up would bound this.
- The subset is extreme-tail by design (hardest-by-rationale-length per category). Five of eight categories returned 0 across all arms because the questions are beyond Opus 4.8's capability ceiling regardless of scaffolding.
- Single-judge methodology mirrors the original HLE paper's grading approach. Judge variance is unbounded at n=1 judge; a 3-judge ensemble would tighten this.

## Dedicated repo

Canonical artifact with full per-agent transcripts and the per-item judge ground truth: [github.com/ejentum/ablation-hle-15](https://github.com/ejentum/ablation-hle-15).

## Files in this directory

| File | Purpose |
|---|---|
| `PRE_REGISTRATION.md` | Predictions committed before any solver ran (SHA `e45aeac5` in dedicated repo) |
| `OBSERVATIONS.md` | Deep corpus analysis: the 3 differentiating questions, canonical-form-selection pattern, prompt-framing confound, missing variables for resolution |
| `RESULTS.md` | Pass-rate scoreboard, per-category breakdown, per-question matrix |
| `CORRECTION.md` | Explanation of the 2026-06-01 aggregate-field correction |
| `raw_scores.json` | Full 45-item per-item judge data (computed pass rates derive from this) |
| `chart.svg` | Three-bar pass-rate chart |
| `workflow.js` | The Claude Code workflow script that orchestrated the 5-phase pipeline (redacted token) |

## Status

Round 2 of the benchmark series. Round 1 lives in [mhpp-10/](../mhpp-10/). Round 3 will be a moderate-difficulty HLE pilot or AIME 2025 focused run, where the model has fighting chance on most questions (the extreme-tail constraint compressed visible separation in this run).
