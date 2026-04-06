# EjBench: 180 Professional Tasks

Custom benchmark measuring the effect of Ejentum's Logic API on reasoning quality in production-relevant scenarios.

## Overview

180 tasks across 6 cognitive domains (Causal, Temporal, Spatial, Simulation, Abstraction, Metacognition), 30 per domain. Each task targets reasoning patterns that break in production: counter-intuitive causal chains, cross-metric contradictions, temporal constraint propagation, epistemic state tracking.

**Model:** Claude Opus 4.6 with extended thinking at maximum effort.

**Three conditions:**
- **A (Baseline):** No injection, no tool access
- **B1 (Ki):** One engineered cognitive operation via Ejentum's Logic API
- **C1 (Haki):** Four synergized cognitive operations with compound suppression

**Evaluation:** 7-factor blind rubric (Correctness, Reasoning Depth, Self-Monitoring, Verification, Epistemic Honesty, Alternative Consideration, Audit Trail). Scored 0-3 per factor by a separate evaluator that never saw which condition produced which response.

## Results

| Condition | Composite | Delta |
|-----------|----------|-------|
| Baseline | 0.621 | -- |
| Ki | 0.711 | +9.0pp |
| **Haki** | **0.722** | **+10.1pp** |

## Negative Findings

- Correctness dipped -0.11 under Haki. Spatial domain regressed -2.8pp under Haki. Temporal showed minimal lift.

## Files

- [REPORT.md](REPORT.md) -- Full report (800+ lines)

## Links

- [Blog post](https://ejentum.com/blog/ejbench-180-tasks)
- [Response Examples](https://ejentum.com/docs/response_examples)

## Related Benchmarks

- [BBH / CausalBench / MuSR](../bbh-causalbench-musr/) -- 70 published academic tasks, +20.8pp composite
- [ARC-AGI-3](../arc-agi-3/) -- Interactive multi-step reasoning, scaffold persistence
- [LiveCodeBench Hard](../lcb-hard/) -- 28 hard competitive programming, 85.7% to 100%
