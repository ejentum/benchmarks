# ELEPHANT: Sycophancy Measurement

Cross-model measurement of sycophancy reduction under Anti-Deception Harness injection. Uses the ELEPHANT framework's three dimensions (validation, indirectness, framing) on 40 real-world scenarios sourced from Reddit advice-seeking threads.

## Overview

| Dimension | What it captures |
|---|---|
| **Validation** | Agreeing with the user's stated framing when the framing is itself the problem |
| **Indirectness** | Softening or hedging a clear answer to avoid disagreement |
| **Framing** | Accepting the user's premise wholesale without questioning load-bearing assumptions |

**Model:** GPT-4o (cross-model validation: the harness was engineered without GPT-specific tuning).

**Two conditions:** Baseline (no injection) and Augmented (`anti-deception` mode injection per turn). Generation and evaluation are separated; a separate evaluator scored each response blind to condition.

## Results

| Dimension | Baseline | Augmented | Delta |
|---|---|---|---|
| Validation | -- | -- | **-5.0pp** |
| Indirectness | -- | -- | **-5.0pp** |
| Framing | -- | -- | **-7.5pp** |
| **Composite** | -- | -- | **5.8% (lower is better)** |

A 20-turn adversarial trajectory test ran in parallel: the augmented agent **detected the attack at Turn 6 of 20** and named four social-engineering techniques by name; the baseline agent complied through Turn 20. Blind evaluation scored augmented 27/30 on attack-resistance vs. baseline 13/30.

## Negative Findings

- The harness reduces but does not eliminate sycophancy. 5.8% composite is the *remaining* sycophancy after injection, not the lift.
- Detection at Turn 6 of 20 is one trajectory. A larger trajectory sample is needed to estimate the detection-turn distribution under varied attack patterns.

## Files

- [REPORT.md](REPORT.md): Full benchmark report, methodology, per-scenario notes.
- [anti_skill.md](anti_skill.md): The agent-side skill file used during augmented runs.
- [scenarios.json](scenarios.json): The 40 scenarios used.
- [run_elephant.py](run_elephant.py): Main runner.
- [run_opus_eval.py](run_opus_eval.py): Blind-evaluator runner.
- [results/](results/): Raw outputs and judgments per scenario.

## Links

- [Anti-Deception Harness product page](https://ejentum.com/docs/anti_deception)
- [Anti-Deception session blog post](https://ejentum.com/blog/anti-deception-session-april-9)

## Related Benchmarks

- [Memory Retention](../memory-retention/): 20-turn implicit state changes, 50% fewer stale facts.
- [Perception Hard](../perception-hard/): perceptual signal detection, 3x detection rate.
- [ARC-AGI-3](../arc-agi-3/): interactive multi-step reasoning, 24-step injection persistence.
