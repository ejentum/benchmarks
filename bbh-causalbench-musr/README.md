# BBH / CausalBench / MuSR: 70 Published Academic Tasks

External validation of Ejentum's Logic API on published benchmarks designed by independent research teams with no knowledge of RA2R.

## Overview

| Source | Tasks | Focus |
|--------|-------|-------|
| **BIG-Bench Hard** (Suzgun et al., 2023) | 25 | Causal judgement, temporal sequences, spatial navigation |
| **CausalBench** | 30 | Abduction, prediction, intervention analysis, counterfactual evaluation |
| **MuSR** (Multistep Soft Reasoning) | 15 | Multi-paragraph narratives requiring theory-of-mind reasoning |

**Model:** Claude Opus 4.6 with extended thinking at maximum effort.

## Results

| Condition | Composite | Delta |
|-----------|----------|-------|
| Baseline | 0.476 | -- |
| **reasoning** | **0.684** | **+20.8pp** |
| reasoning-multi | 0.562 | +8.6pp |

Single mode dominated on focused tasks. Multi correctness dropped -0.12. Spatial navigation regressed -20.0pp under reasoning-multi (5 tasks).

## Files

- [REPORT.md](REPORT.md) -- Full report (640+ lines)

## Links

- [Blog post](https://ejentum.com/blog/bbh-causalbench-musr-benchmark)

## Related Benchmarks

- [EjBench](../ejbench/) -- 180 custom professional tasks, +10.1pp composite
- [ARC-AGI-3](../arc-agi-3/) -- Interactive multi-step reasoning, injection persistence
- [LiveCodeBench Hard](../lcb-hard/) -- 28 hard competitive programming, 85.7% to 100%
