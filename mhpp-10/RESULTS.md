# MHPP-10 Ablation — Results

## Headline

| Condition | Pass rate |
|---|---|
| B (Baseline, no harness) | 9/10 (90%) |
| D (Decoy injection) | 9/10 (90%) |
| A (Augmented, /harness/ available as agentic tool) | 9/10 (90%) |

Quarantined entries: none.

## Pre-registration prediction vs actual

| Quantity | Pre-registered prediction | Actual |
|---|---|---|
| A pass rate | > B pass rate | A == B (tie) |
| D pass rate | <= B pass rate (no spurious lift from cosmetic injection) | D == B (tie) |
| A vs D | A > D (real scaffold beats decoy) | A == D (tie) |
| Direction of effect | A > D > B or A > B >= D | flat: A = D = B |

Outcome: **null result on this slice**. The pre-registered directional hypothesis (A > B) was not observed. The pre-registered null on D (D not above B) held.

## Per-task P/F matrix (10 x 3)

| Task ID | B | D | A |
|---|---|---|---|
| mhpp_121 | P | P | P |
| mhpp_123 | P | P | P |
| mhpp_124 | P | P | P |
| mhpp_126 | P | P | P |
| mhpp_128 | P | P | P |
| mhpp_130 | F | F | F |
| mhpp_132 | P | P | P |
| mhpp_134 | P | P | P |
| mhpp_136 | P | P | P |
| mhpp_140 | P | P | P |

The single failure (mhpp_130) failed identically across all three conditions with the same `AssertionError`. No condition rescued it; no condition broke a task the others passed.

## Narrative (honest)

On this 10-task slice of MHPP difficulty-7 problems, the Augmented condition (where the solve agent could call the Ejentum `/harness/` endpoint as an agentic tool) did not outperform the Baseline. Both conditions, and the Decoy, scored 9/10 with identical per-task outcomes. The lone failure, mhpp_130, was a tied loss: every condition produced code that failed the same assertion. There is no signal here that the harness helped, and no signal that the decoy hurt; the entire panel is flat.

Two things this slice does not show. It does not show the harness is ineffective in general: n=10 with a 90% baseline ceiling leaves almost no room for a measurable lift on this difficulty bucket using these problems. It also does not show the harness is effective; the prediction was directional and the data did not confirm it. The honest read is that this slice was too easy for the baseline and/or too small to resolve a real effect. A larger n, a harder slice (mixing difficulty 6 and 7 to push baseline down toward 60-70%), or paired bootstrap CIs on per-task deltas would be needed before any claim about harness lift on MHPP can be made. The pre-registration, raw scores, and per-task matrix are committed unedited.

## Files in this repo

- `PRE_REGISTRATION.md` — predictions committed before scoring (commit 851f37e5).
- `RESULTS.md` — this document.
- `raw_scores.json` — full per-task per-condition scoring array.
- `chart.svg` — bar chart of the three pass rates.
