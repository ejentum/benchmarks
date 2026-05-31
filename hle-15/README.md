# HLE-15 Ablation

Reasoning Harness benchmark. 15 text-only multiple-choice questions from Humanity's Last Exam, Claude Opus 4.8, B/D/A conditions. Pre-registered ladder A > D > B before any solver ran. This is Round 2 of the Ejentum harness ablation series; Round 1 saturated on MHPP-10 (9/10 across all conditions), so Round 2 moved to a non-saturated frontier benchmark to test whether the harness produces visible pass-rate spread when the model has headroom to fail.

## Headline pass rates

| Arm | Description | Pass rate |
|---|---|---|
| **B** | Bare model, no harness | **4 / 15 (26.7%)** |
| **D** | Dynamic harness (retrieval only) | **4 / 15 (26.7%)** |
| **A** | Adaptive harness (retrieval + adapter) | **2 / 15 (13.3%)** |

## Findings

- Observed ordering is B = D > A. The pre-registered prediction (A > D > B) was not validated on this benchmark; the adaptive arm regressed two raw passes below the bare model.
- D matched B exactly at 4/15. Retrieval-only injection neither helped nor hurt pass rate at HLE difficulty.
- Per-category breakdown shows the three arms collapse to identical scores in 7 of 8 categories. Math is the only category that differentiated: A scored 2/3, B and D each 1/3. Humanities, Chemistry, Engineering, and Other returned zero across all arms.
- Cross-reference to Round 1 ([MHPP-10](../mhpp-10/)): pass rate saturated there at 9/9/9, and the A > D > B ordering was visible only in blind expert qualitative review, not in the aggregate. Round 2 tested the opposite regime (non-saturated, frontier) and pass-rate spread emerged in the wrong direction.
- With 4 passes per arm spread across 8 categories, a single item flip moves the headline. The result is real but the confidence interval is wide; the adaptive regression is the part that warrants direct investigation rather than re-framing.

## Dedicated repo

Canonical artifact with full per-agent transcripts, judge outputs, and the pre-registration commit: [github.com/ejentum/ablation-hle-15](https://github.com/ejentum/ablation-hle-15). This subdir is the indexed entry in the benchmark series; the dedicated repo is the source of record.

## File inventory

| File | Purpose |
|---|---|
| `PRE_REGISTRATION.md` | Pre-registration document committed before any solver ran. Specifies the four hypotheses (H1-H4), pinned HLE indices, scoring rules, and quarantine criteria. |
| `RESULTS.md` | Round 2 results report: headline pass rates, Round 1 vs Round 2 side-by-side, per-category breakdown, and ~300-word honest interpretation. |
| `raw_scores.json` | Per-question per-arm raw pass/fail scores for the 15 pinned HLE items. |
| `chart.svg` | Headline bar chart of B/D/A pass rates. |
| `workflow.js` | n8n workflow source used to dispatch the 45 solver agents (3 arms x 15 questions). HF token redacted; set your own `HF_TOKEN` to reproduce. |

## Reproducibility

The `workflow.js` script is the exact n8n workflow used to run the ablation: 15 pinned HLE indices, three arms (B/D/A), 45 solve agents total, exact-letter scoring on the multiple-choice subset (no judge agent). To reproduce, import the workflow into n8n, set your `HF_TOKEN` environment variable for the `cais/hle` dataset load, and dispatch. The pinned indices are `[2431, 865, 1968, 42, 874, 334, 914, 2466, 2448, 2414, 1786, 2407, 2492, 1990, 2418]`.

## Status

Round 2 of the Ejentum harness benchmark series. Round 1 (MHPP-10, code modes, 128-ability pool) lives at [`../mhpp-10/`](../mhpp-10/). Round 2 (this run, reasoning + adaptive-reasoning modes, 311-ability pool) is the first non-saturated test in the series.
