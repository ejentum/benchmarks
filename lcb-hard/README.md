# LiveCodeBench Hard: RA2R Logic API on Competitive Programming

Claude Opus 4.6 with maximum-effort extended thinking solves 85.7% of 28 hard AtCoder problems. With one Ejentum Logic API call per task, it solves **100%**.

## Results

| Condition | Passed | Rate |
|-----------|--------|------|
| Baseline (Opus 4.6 max effort) | 24/28 | 85.7% |
| + Logic API injection | 28/28 | **100.0%** |
| **Delta** | **+4** | **+14.3pp** |

**Zero regressions.** Every task that passed baseline also passed augmented.

## Blind Evaluation

A blind evaluator scored both solutions per task without knowing which used the injection:

- **3.5x magnitude asymmetry.** Average injection win: +5.7 points. Average baseline win: -1.6 points.
- **Never loses on correctness (2-0) or robustness (4-0).**
- **Independent bug discovery.** The evaluator traced a fatal sentinel-collision bug in the baseline, scored it 2/10, without knowing which solution used the injection.

## Repository Structure

```
README.md           This file
REPORT.md           Full benchmark report (296 lines, 13 sections)
skill.md            The Logic API skill file used in the benchmark
run_lcb.py          Benchmark runner (reproducible)
results/
  baseline.json     28 baseline results (metadata, no code)
  augmented.json    28 augmented results (metadata, no code)
  blind_eval.json   27 blind evaluation results with full commentary
  three_way_evals.json   2 three-way blind evaluations
```

## Reproduction

Requires an Ejentum API key ([ejentum.com](https://ejentum.com)) and Claude CLI.

```bash
# Install dependencies
pip install httpx

# Set your API key
export EJENTUM_API_KEY="your-key-here"

# Run baseline
python run_lcb.py --condition baseline --run-id my_run

# Run augmented
python run_lcb.py --condition augmented --run-id my_run
```

Task data is not included (LiveCodeBench IP). Download from the [LiveCodeBench HuggingFace dataset](https://huggingface.co/datasets/livecodebench/code_generation) and place batch files in the same directory.

## Links

- [Benchmark report (blog)](https://ejentum.com/blog/livecodebench-hard-28-tasks)
- [Observations post](https://ejentum.com/blog/what-we-saw-when-opus-thought-harder)
- [Logic API skill files](https://ejentum.com/docs/skill_unified)
- [Ejentum](https://ejentum.com)
