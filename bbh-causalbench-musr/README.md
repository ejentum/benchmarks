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
| **Ki** | **0.684** | **+20.8pp** |
| Haki | 0.562 | +8.6pp |

Ki dominated on focused tasks. Haki correctness dropped -0.12. Spatial navigation regressed -20.0pp under Haki (5 tasks).

## Files

- [REPORT.md](REPORT.md) -- Full report (640+ lines)

## Links

- [Blog post](https://ejentum.com/blog/bbh-causalbench-musr-benchmark)
