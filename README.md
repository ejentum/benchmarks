# Ejentum Benchmarks

Benchmark methodology, evaluation results, and raw data for [Ejentum's Logic API](https://ejentum.com) -- reasoning infrastructure for AI agents.

The Logic API retrieves engineered cognitive operations (not information) and injects them into an LLM's context at inference time. These benchmarks measure the behavioral effect of that injection across three independent evaluation frameworks.

---

## Research Paper

**Under Pressure: RA²R and the Emergence of Uninstructed Reasoning Behaviors in Scaffold-Augmented Language Models**

Franko Luci, Ejentum. April 2026.

This paper synthesizes all benchmark findings into a unified thesis: suppression is pressure, and emergence is the model's response. 25 pages, 9 figures, all negative findings reported.

- **[Download PDF](research/paper/under_pressure.pdf)**
- **Zenodo:** [10.5281/zenodo.19392715](https://doi.org/10.5281/zenodo.19392715)
- **SSRN:** [Abstract ID 6512038](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6512038)
- **ORCID:** [0009-0000-7086-6991](https://orcid.org/0009-0000-7086-6991)
- **Blog post:** [ejentum.com/blog/under-pressure-research-paper](https://ejentum.com/blog/under-pressure-research-paper)

---

## What Was Tested

| Benchmark | Tasks | Type | Model | Primary Finding |
|-----------|-------|------|-------|-----------------|
| [EjBench](ejbench/) | 180 custom professional | Single-turn, 7-factor blind rubric | Claude Opus 4.6 | +10.1pp composite quality lift. Self-monitoring nearly doubled. Correctness flat. |
| [BBH / CausalBench / MuSR](bbh-causalbench-musr/) | 70 published academic | Single-turn, 7-factor blind rubric | Claude Opus 4.6 | +20.8pp composite lift on focused tasks. Correctness improved +7.1pp. |
| [ARC-AGI-3](arc-agi-3/) | 25 steps x 2 conditions | Interactive multi-step reasoning | Claude Sonnet 4.6 | RHAE 0.0 = 0.0 (both failed). Scaffold persisted 24 steps. Memory decay reversed. |
| [LiveCodeBench Hard](lcb-hard/) | 28 hard competitive programming | Code generation + correctness | Claude Opus 4.6 (max effort) | **85.7% -> 100%. +14.3pp. 4 tasks gained, 0 lost. Zero regressions.** |

**Total: 250 single-turn tasks + 50 interactive reasoning steps + 28 competitive programming tasks across four independent benchmarks.**

---

## How It Was Tested

All benchmarks follow the same protocol:

1. **Agent-native execution.** Agents called Ejentum's production Logic API themselves via tool use. The agent summarized the task, called the endpoint, received the scaffold, and applied it before reasoning. This mirrors real deployment -- the retrieval variance is real, not simulated.

2. **Three conditions per task.** A (baseline, no injection), B1 (Ki -- one engineered cognitive operation), C1 (Haki -- four synergized operations with compound suppression).

3. **Blind evaluation.** A separate evaluator scored outputs on a 7-factor rubric without knowing which condition produced which response. Generation and evaluation are separate stages.

4. **Negative findings reported.** Correctness dips, domain regressions, and unexpected contradiction increases are in the reports. We do not omit results that challenge the thesis.

---

## Key Terms

| Term | Definition |
|------|-----------|
| **Logic API** | Ejentum's REST endpoint (`POST /logicv1/`). Retrieves engineered cognitive operations from 311 abilities organized across six reasoning dimensions. |
| **Scaffold** | A structured reasoning injection containing a negative gate (failure pattern to avoid), reasoning topology (execution structure), suppression signals (failure modes to block), amplification signals (patterns to prioritize), and a falsification test (verification criterion). Optimized for agentic inference. |
| **Ki** | Single-ability mode. One scaffold per API call. Highest signal density per token. |
| **Haki** | Multi-ability mode. Four synergized scaffolds per API call with compound suppression. Covers cross-dimensional reasoning. |
| **Suppression** | Named failure modes injected as constraints. Suppression signals reduce the probability of specific reasoning shortcuts (e.g., `surface_level_stop`, `single_variable_fixation`). In testing, suppression produces larger behavioral effects than amplification alone. |

---

## Headline Results

### Quality Lift (7-factor composite)

| Benchmark | Baseline | Best Condition | Delta |
|-----------|----------|---------------|-------|
| EjBench (180 tasks) | 0.621 | 0.722 (Haki) | **+10.1pp** |
| BBH/CausalBench/MuSR (70 tasks) | 0.476 | 0.684 (Ki) | **+20.8pp** |

### Per-Factor (largest improvements)

| Factor | EjBench Lift | BBH Lift |
|--------|-------------|----------|
| Self-Monitoring | +92% | +134% |
| Verification | +45% | +84% |
| Alternative Consideration | +35% | +66% |
| Epistemic Honesty | +26% | +37% |

### ARC-AGI-3 Process Metrics

| Metric | Baseline | Augmented |
|--------|----------|-----------|
| Memory decay slope | -0.005 (degrading) | +0.014 (improving) |
| Scaffold half-life | 0 | 24 steps |
| Reasoning depth trend | 0.86 | 10.50 (12.2x) |
| Stuck episodes | 2 | 1 (50% fewer) |

---

## Negative Findings

- **Correctness dipped under Haki on EjBench** (-0.11 on 3-point scale). Thorougher reasoning occasionally trades accuracy for caution.
- **Spatial domain regressed under Haki on BBH** (-20.0pp on 5 tasks). Multi-perspective injection confused spatial constraint tracking.
- **Haki correctness dropped on BBH** (-0.12). Focused tasks need focused scaffolds. Ki outperformed Haki on every single-domain task.
- **Contradiction rate increased 1.9x on ARC-AGI-3** (token-normalized). Whether this is productive cognitive conflict or destructive interference is unresolved.
- **ARC-AGI-3: RHAE 0.0 = 0.0.** Neither condition cleared Level 0. All process metrics are measured in a failure context.

---

## What Would Falsify This

The core claim is that structured reasoning injection produces measurable behavioral changes in LLM outputs. This claim is falsified if:

1. The same injection format produces zero behavioral change on a different model family (e.g., GPT, Gemini, Llama).
2. Random scaffold injection (shuffled suppression signals, mismatched topologies) produces equivalent lift -- meaning the specific cognitive operation doesn't matter.
3. The 7-factor rubric scoring shows evaluator bias that systematically inflates injected conditions.
4. Replication on a second independent run produces directionally different results.

We have not yet tested conditions 1 or 2. Condition 3 is partially addressed by the blind protocol but not fully eliminated (LLM-as-judge). Condition 4 is partially addressed by the BBH correctness-only replication (two independent runs, consistent direction).

---

## Limitations

- **One model family.** All results are on Claude (Opus 4.6 for single-turn, Sonnet 4.6 for ARC-AGI-3). Generalization to other model families is expected but not tested.
- **LLM-as-judge.** Two-stage blind protocol: generation and evaluation are separate stages. The evaluator never saw which condition produced which output. Human evaluation on a subset would strengthen the evidence.
- **Custom task design bias.** EjBench tasks were designed by Ejentum. The BBH/CausalBench/MuSR benchmark addresses this with externally designed tasks.
- **Single evaluation run.** EjBench and ARC-AGI-3 have each been run once. BBH correctness was replicated across two runs.
- **Small samples on sub-analyses.** Spatial navigation regression rests on 5 tasks. ARC-AGI-3 is n=1 per condition.

---

## Repository Structure

```
benchmarks/
  README.md
  LICENSE
  ejbench/
    README.md
    REPORT.md
    generations/              # 540 cleaned model outputs (A/B1/C1 per task)
    judgments/                # 538 rubric scores (7 factors per output)
    results/                  # Aggregated multifactor results, retrieval precision
  bbh-causalbench-musr/
    README.md
    REPORT.md
    generations/              # 850 cleaned model outputs
    judgments/                # 209 rubric scores
    results/                  # Aggregated multifactor results
  arc-agi-3/
    README.md
    SCIENTIFIC_REPORT.md
    BENCHMARK.md
    COMPLIANCE_AUDIT.md
    STUDY_PROTOCOL.md
    SYSTEM_PROMPTS.md
    RESEARCH.md
    results/
      all_metrics.json
      A_baseline__ls20.json   # Full 25-step action log with reasoning text
      B_augmented__ls20.json  # Full 25-step action log with RA2R queries
      REPORT.md
  research/
    COGNITIVE_SCAFFOLDING_THESIS.md
    VALIDATED_CLAIMS.md
```

---

## Links

- **Product:** [ejentum.com](https://ejentum.com)
- **Documentation:** [ejentum.com/docs](https://ejentum.com/docs)
- **Skill file (tool-use doc):** [ejentum.com/docs/agent_skill](https://ejentum.com/docs/agent_skill)
- **Blog:** [ejentum.com/blog](https://ejentum.com/blog)
- **29 benchmark tasks with outputs:** [ejentum.com/use-cases/tasks](https://ejentum.com/use-cases/tasks)
- **ARC-AGI-3 trace study:** [ejentum.com/tasks/ARC-LS20-TRACE](https://ejentum.com/tasks/ARC-LS20-TRACE)
- **LiveCodeBench Hard report:** [ejentum.com/blog/livecodebench-hard-28-tasks](https://ejentum.com/blog/livecodebench-hard-28-tasks)
- **LiveCodeBench Hard observations:** [ejentum.com/blog/what-we-saw-when-opus-thought-harder](https://ejentum.com/blog/what-we-saw-when-opus-thought-harder)
- **Integration examples:** [github.com/ejentum/examples](https://github.com/ejentum/examples)

---

## License

Released under [CC BY 4.0](LICENSE). Share and adapt with attribution.
