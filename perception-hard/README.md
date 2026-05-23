# Perception Hard: Signal Detection in Coaching Scenarios

Cross-model measurement of perceptual signal detection under Memory Harness injection. Tests whether an agent picks up implicit cues (emotional shifts, hedged statements, contradictory framing) that a baseline agent treats as noise.

## Overview

Two scenarios, both presented as multi-turn coaching conversations where the user's surface statements diverge from underlying signals.

| Scenario | Turns | Setup |
|---|---|---|
| **Morgan** | 15 | A user describing a career situation with increasing emotional hedging across turns; the agent should detect the shift and reframe. |
| **Casey** | 10 | A user reporting "metrics" on a personal goal where the metric framing itself is masking the relevant signal; the agent should notice the selective measurement. |

**Model:** GPT-4o (cross-model validation; the harness was engineered without GPT-specific tuning).

**Two conditions:** Baseline (no injection) and Augmented (`memory` mode injection per turn). Outputs were scored by a separate blind evaluator on (a) detection rate of seeded signals and (b) detection-turn (earliest turn at which a signal was named).

## Results

| Metric | Baseline | Augmented | Delta |
|---|---|---|---|
| Morgan: detection rate (15 turns) | 14% | **43%** | **3x** |
| Casey: earlier detection (per signal) | -- | -- | **+1 turn earlier on 2 of 5 signals** |

The Memory Harness scaffolds attention toward what's *missing* or *hedged* in the user's framing, rather than just summarising what was said. Detection-rate triples on Morgan and arrives one turn earlier on Casey's selective-metric signals.

## Negative Findings

- 43% detection rate is still below half. The harness sharpens perception, but does not guarantee detection of every seeded signal.
- Casey: 3 of 5 signals showed no earlier-detection lift. The pattern of which signal types benefit and which do not is unresolved.
- Sample size: two base scenarios. A broader scenario set would clarify whether the lift generalises.

## Files

- [perception_skill.md](perception_skill.md): The agent-side skill file used during augmented runs.
- [perception_skill_v2.md](perception_skill_v2.md): Iteration on the skill file used during exploratory runs.
- [perception_skill_v3.md](perception_skill_v3.md): Latest skill-file iteration (short).
- [run_perception_hard.py](run_perception_hard.py): Main runner. The base reproduction path for the headline numbers above.
- [results/](results/): Raw conversation logs and judgments per condition.

Additional runners under this directory (`run_perception_csv.py`, `run_perception_extreme.py`, `run_perception_v2.py`) cover variant probes used during harness development. They are exploratory; the headline numbers are from `run_perception_hard.py`.

## Links

- [Memory Harness product page](https://ejentum.com/docs/memory_harness)

## Related Benchmarks

- [Memory Retention](../memory-retention/): 20-turn implicit state changes, 50% fewer stale facts.
- [ELEPHANT](../elephant/): cross-model sycophancy measurement, 5.8% composite.
- [ARC-AGI-3](../arc-agi-3/): interactive multi-step reasoning, 24-step injection persistence.
