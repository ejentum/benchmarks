# ARC-AGI-3: Interactive Reasoning Benchmark

Trace-level comparison of a frontier LLM playing ARC-AGI-3 game LS20 under two conditions: raw baseline and augmented with Ejentum's Logic API.

## Overview

ARC-AGI-3 is the world's only unbeaten AI benchmark. Frontier model performance: 0.26%.

**Game:** LS20 (ls20-9607627b). Keyboard-controlled spatial navigation, 7 levels. Human baseline: 21 actions for Level 0.

**Model:** Claude Sonnet 4.6 with extended thinking at maximum effort.

**Two conditions:** Baseline (no scaffold) vs Augmented (Logic API as callable tool). 25 steps each. Same game, same seed.

## Results

RHAE 0.0 = 0.0. Neither condition cleared Level 0. The evidence is in the reasoning process:

| Metric | Baseline | Augmented |
|--------|----------|-----------|
| Memory decay slope | -0.005 | +0.014 (reversed) |
| Scaffold half-life | 0 | 24 steps |
| Reasoning depth trend | 0.86 | 10.50 (12.2x) |
| Stuck episodes | 2 | 1 (50% fewer) |

**Limitations:** n=1 per condition. Contradiction rate increased 1.9x.

## Files

| File | Description |
|------|-------------|
| [SCIENTIFIC_REPORT.md](SCIENTIFIC_REPORT.md) | Full trace-level analysis (625 lines) |
| [BENCHMARK.md](BENCHMARK.md) | Architecture overview |
| [COMPLIANCE_AUDIT.md](COMPLIANCE_AUDIT.md) | ARC-AGI-3 spec verification |
| [STUDY_PROTOCOL.md](STUDY_PROTOCOL.md) | Experimental design |
| [RESEARCH.md](RESEARCH.md) | Scoring corrections, frontier model context |
| [results/all_metrics.json](results/all_metrics.json) | Raw metrics (both conditions) |
| [results/REPORT.md](results/REPORT.md) | Executive summary |

## Links

- [Blog: Full report](https://ejentum.com/blog/arc-agi-3-benchmark-report)
- [Blog: Emergent behaviors](https://ejentum.com/blog/arc-agi-3-emergent-behaviors)
- [Live trace study](https://ejentum.com/tasks/ARC-LS20-TRACE)

## Related Benchmarks

- [EjBench](../ejbench/) -- 180 custom professional tasks, +10.1pp composite
- [BBH / CausalBench / MuSR](../bbh-causalbench-musr/) -- 70 published academic tasks, +20.8pp composite
- [LiveCodeBench Hard](../lcb-hard/) -- 28 hard competitive programming, 85.7% to 100%
