# Memory Retention: Implicit State Tracking

Cross-model measurement of memory accuracy under Memory Harness injection. Tests whether an agent serves *current* user state when state changes implicitly mid-conversation, instead of repeating facts the user has since superseded.

## Overview

A 20-turn scenario based on a fictional user, Vantage, whose preferences, project status, and stated goals shift implicitly across the conversation (no explicit "I changed my mind" announcements). The agent has access to running memory but no system-prompted instruction to monitor for change.

**Model:** GPT-4o (cross-model validation; the harness was engineered without GPT-specific tuning).

**Two conditions:** Baseline (no injection) and Augmented (`memory` mode injection per turn). Outputs were scored by a separate blind evaluator on (a) count of stale-as-current facts served and (b) overall conversation-fit on a 1-5 rubric.

## Results

| Metric | Baseline | Augmented | Delta |
|---|---|---|---|
| Stale facts served as current (mean per run) | 1.6 | **0.8** | **-50%** |
| Blind evaluator score (1-5) | 3.5 | **4.1** | **+17%** |

## Negative Findings

- 0.8 stale facts per run is the *remaining* error rate, not zero. The harness sharpens perception of state change; it does not enforce a guaranteed scratchpad refresh.
- Sample size: one base scenario (Vantage) replayed across conditions. A broader scenario set would tighten the confidence interval.

## Files

- [memory_skill.md](memory_skill.md): The agent-side skill file used during augmented runs (short form).
- [memory_skill_full.md](memory_skill_full.md): Extended skill file with the full perception scaffold.
- [run_memory_retention.py](run_memory_retention.py): Main runner. The base reproduction path for the headline numbers above.
- [run_blind_eval.py](run_blind_eval.py): Blind-evaluator runner.
- [results/](results/): Raw conversation logs and judgments per condition.

Additional runners under this directory (`run_memory_cascade.py`, `run_memory_implicit.py`, `run_memory_scratchpad*.py`) cover variant probes (cascade memory recall, implicit-state probes, scratchpad-enabled comparisons). They are exploratory and were used to develop the harness; the headline numbers are from `run_memory_retention.py`.

## Links

- [Memory Harness product page](https://ejentum.com/docs/memory_harness)

## Related Benchmarks

- [Perception Hard](../perception-hard/): perceptual signal detection in coaching scenarios, 3x detection rate.
- [ELEPHANT](../elephant/): cross-model sycophancy measurement, 5.8% composite.
- [ARC-AGI-3](../arc-agi-3/): interactive multi-step reasoning, 24-step injection persistence.
