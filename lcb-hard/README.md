# LiveCodeBench Hard: 28 Hard Competitive Programming Tasks

Evaluation of Ejentum's Logic API on 28 hard competitive programming tasks from [LiveCodeBench](https://livecodebench.github.io/), all sourced from AtCoder.

## Overview

**Model:** Claude Opus 4.6 with maximum-effort extended thinking.

**Two conditions:**
- **Baseline:** Standard competitive programming prompt. No augmentation.
- **Augmented:** Ejentum Logic API [skill file](https://ejentum.com/docs/agent_skill) with forced API call on all hard tasks. Decision pass generates query, scaffold injected before code generation.

**Evaluation:** Exact string match on public test cases (2-4 per task). Pass = all tests pass.

## Results

| Condition | Passed | Rate |
|-----------|--------|------|
| Baseline | 24/28 | 85.7% |
| **Augmented** | **28/28** | **100.0%** |
| **Delta** | **+4** | **+14.3pp** |

**Zero regressions.** Every task baseline passes, augmented also passes.

## Tasks Gained (fail -> pass)

| Task | Baseline Failure | Scaffold Fix |
|------|-----------------|--------------|
| Art Gallery on Graph | Wrong answer (1/3 tests) | Suppression prevented premature graph traversal |
| Best Performances | Reasoning spiral (610s, zero code) | Topology provided convergence structure |
| Tangency of Cuboids | Reasoning spiral (1190s, zero code) | Structured 3D spatial reasoning |
| Roulettes | Precision mismatch | Algorithm correct, formatting corrected |

## Key Findings

- **100% rescue rate on reasoning spirals** — 2/2 tasks where baseline thinking spiraled without producing code
- **Zero identical solutions** — all 24 both-pass tasks produced different code (avg Jaccard similarity 0.689)
- **2.0% more concise code** across shared tasks
- **33% fewer inline comments** — deliberate coding shift
- **Algorithm enrichment** on 4/24 tasks (added BFS, binary search, sorting)
- **One task faster** — Defect: 515s baseline -> 374s augmented (-27%)
- **Consistent** across 3 independent batches, zero regressions in any batch

## Files

| Path | Description |
|------|-------------|
| `REPORT.md` | Full research report with forensic analysis |
| `run_lcb.py` | Benchmark runner (requires Ejentum API key) |
| `results/baseline/results.json` | 28 baseline results (metadata, no code) |
| `results/augmented/results.json` | 28 augmented results (metadata + scaffold stats, no code) |

## Methodology

Full methodology documented in [REPORT.md](REPORT.md). Blog posts:
- [Benchmark Report](https://ejentum.com/blog/livecodebench-hard-28-tasks)
- [Observations](https://ejentum.com/blog/what-we-saw-when-opus-thought-harder)

## Reproduce

```bash
export EJENTUM_API_KEY="your-api-key"
python run_lcb.py --condition baseline --run-id my_run
python run_lcb.py --condition augmented --run-id my_run
```

Requires: Python 3.11+, `httpx`, Claude CLI (`claude`), Ejentum API key ([get one free](https://ejentum.com/pricing)).

**Note:** Task data (`lcb_tasks.json`) is not included in this repository — tasks are sourced from [LiveCodeBench](https://livecodebench.github.io/) and are their intellectual property. To reproduce, download hard tasks from the LiveCodeBench HuggingFace dataset (`livecodebench/code_generation`) and save as `lcb_tasks.json`. The [skill file](https://ejentum.com/docs/agent_skill) (`skill.md`) is available from Ejentum's documentation.
