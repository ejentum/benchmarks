# Round 2 Results: HLE-15, Opus 4.8, Reasoning Mode

**Benchmark:** Humanity's Last Exam (HLE), 15 pinned items from the `cais/hle` test split
**Model:** Claude Opus 4.8
**Harness mode:** reasoning
**Pinned indices:** [2431, 865, 1968, 42, 874, 334, 914, 2466, 2448, 2414, 1786, 2407, 2492, 1990, 2418]
**Pre-registration:** [PRE_REGISTRATION.md](./PRE_REGISTRATION.md) (commit e45aeac)
**Round 1 reference:** [ejentum/ablation-mhpp-10](https://github.com/ejentum/ablation-mhpp-10)

## Headline pass rates

| Arm | Description | Pass rate |
|---|---|---|
| **B** | Bare model, no harness | **4 / 15 (26.7%)** |
| **D** | Dynamic harness (retrieval only) | **4 / 15 (26.7%)** |
| **A** | Adaptive harness (retrieval + adapter) | **2 / 15 (13.3%)** |

## Round 1 vs Round 2 side-by-side

| Arm | Round 1: MHPP-10 (code mode, saturated) | Round 2: HLE-15 (reasoning mode, frontier) |
|---|---|---|
| B (bare) | 9 / 10 (90%) | 4 / 15 (26.7%) |
| D (dynamic) | 9 / 10 (90%) | 4 / 15 (26.7%) |
| A (adaptive) | 9 / 10 (90%) | 2 / 15 (13.3%) |
| Blind expert ordering | A > D > B (8/9 ballots) | n/a this round |

Round 1 was saturated: all three arms scored 9/10 on MHPP-10, and the harness lift was visible only in blind qualitative review, not in the pass-rate aggregate. Round 2 tests the opposite regime: a frontier benchmark Opus 4.8 has not saturated.

## Pre-registration prediction vs actual

Pre-registration specified four hypotheses:

- **H1:** A > D > B with measurable spread (full product validated)
- **H2:** A roughly D, both > B (retrieval matters, adapter contribution small)
- **H3:** No separation across arms (harness does not lift HLE pass rate at this capability level)
- **H4:** B > D or B > A (harness misroutes; investigate)

**Observed:** B = D > A. This is closest to **H4 (inverted)** with respect to A specifically, while D ties B exactly. The adaptive arm underperformed both the bare model and the retrieval-only arm.

## Per-category breakdown

| Category | n | B | D | A |
|---|---|---|---|---|
| Math | 3 | 1/3 | 1/3 | 2/3 |
| Biology/Medicine | 2 | 1/2 | 1/2 | 1/2 |
| Computer Science / AI | 2 | 1/2 | 1/2 | 1/2 |
| Physics | 2 | 1/2 | 1/2 | 1/2 |
| Humanities/Social Science | 2 | 0/2 | 0/2 | 0/2 |
| Chemistry | 2 | 0/2 | 0/2 | 0/2 |
| Engineering | 1 | 0/1 | 0/1 | 0/1 |
| Other | 1 | 0/1 | 0/1 | 0/1 |
| **Total** | **15** | **4/15** | **4/15** | **2/15** |

The only category where any arm differentiates is Math: A scored 2/3, B and D each scored 1/3. Every non-math category produced identical scores across the three arms, with Humanities, Chemistry, Engineering, and Other returning zero passes for all arms.

## Honest interpretation (~300 words)

Round 1 told us the harness was a quality lift the aggregate could not see: three identical 9/10 scores, with blind expert reviewers separating A > D > B in 8 of 9 ballots. Round 2 was designed to ask the opposite question. If we move from a saturated benchmark to a frontier one Opus 4.8 has not solved, does the harness lift pass rate, or was Round 1's expert preference an artifact of a regime where all answers were already correct and reviewers were sorting on style?

The honest read is that **at HLE difficulty, the harness did not lift pass rate, and the adaptive arm regressed**. D matched B at 4/15. A came in at 2/15, two raw passes below the bare model. This is closest to H4 (inverted) for the adaptive arm: the adapter actively cost us on a subset of items the bare model handled. The only signal in the other direction is Math, where A picked up one extra pass that B and D missed. Everywhere else the three arms collapse to the same per-category numbers, including six straight zeros in the long-tail categories (Humanities, Chemistry, Engineering, Other).

What this does and does not mean. It does not invalidate Round 1: code-mode lift on a saturated benchmark is a different claim from reasoning-mode lift on a frontier benchmark, and the regimes are genuinely different. It does mean the harness's value proposition at HLE-class difficulty needs to be re-examined: either the retrieval is targeting the wrong abilities for HLE's question distribution, the adapter is overwriting reasoning steps the bare model would have gotten right, or the n is too small to separate signal from variance at a 13-27% pass rate band. With four passes per arm spread across eight categories, a single item flip moves the headline. The result is real but the confidence interval is wide; the adaptive regression on A is the part that warrants direct investigation rather than re-framing.

## Quarantined entries

None. All 15 items resolved cleanly; no entries quarantined from scoring.

## Cross-links

- Round 1 repo (code mode, saturated): https://github.com/ejentum/ablation-mhpp-10
- Round 2 repo (this run): https://github.com/ejentum/ablation-hle-15
- Pre-registration: [PRE_REGISTRATION.md](./PRE_REGISTRATION.md)
- Harness: https://ejentum.com
