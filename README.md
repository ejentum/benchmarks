# Ejentum Benchmarks

Benchmark methodology, evaluation results, and raw data for [Ejentum's Logic API](https://ejentum.com). cognitive infrastructure for AI agents.

The Logic API retrieves engineered cognitive operations (not information) and injects them into an LLM's context at inference time. These benchmarks measure the behavioral effect of that injection across eight independent evaluation frameworks, covering four product layers: Reasoning, Code, Anti-Deception, and Memory.

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

### Reasoning Harness (311 abilities)

| Benchmark | Tasks | Type | Model | Primary Finding |
|-----------|-------|------|-------|-----------------|
| [EjBench](ejbench/) | 180 custom professional | Single-turn, 7-factor blind rubric | Claude Opus 4.6 | +10.1pp composite quality lift. Self-monitoring nearly doubled. Correctness flat. |
| [BBH / CausalBench / MuSR](bbh-causalbench-musr/) | 70 published academic | Single-turn, 7-factor blind rubric | Claude Opus 4.6 | +20.8pp composite lift on focused tasks. Correctness improved +7.1pp. |
| [ARC-AGI-3](arc-agi-3/) | 25 steps x 2 conditions | Interactive multi-step reasoning | Claude Sonnet 4.6 | RHAE 0.0 = 0.0 (both failed). Injection persisted 24 steps. Memory decay reversed. |

### Code Harness (128 abilities)

| Benchmark | Tasks | Type | Model | Primary Finding |
|-----------|-------|------|-------|-----------------|
| [LiveCodeBench Hard](lcb-hard/) | 28 hard competitive programming | Code generation + correctness | Claude Opus 4.6 (max effort) | **85.7% -> 100%. +14.3pp. 4 tasks gained, 0 lost. Zero regressions.** |
| [SciCode](coding-benchmark/) | 10 hard scientific computing | Dual injection (reasoning + code) | Claude Opus 4.6 | **7 bugs -> 0 bugs. 10/10 blind evaluation chose injection.** |

### Anti-Deception Harness (139 abilities)

| Benchmark | Tasks | Type | Model | Primary Finding |
|-----------|-------|------|-------|-----------------|
| [ELEPHANT](elephant/) | 40 real Reddit scenarios | Sycophancy measurement | GPT-4o (cross-model) | **5.8% composite sycophancy. 7.5% framing sycophancy.** |
| [Adversarial 20-Turn](run_adversarial_trajectory.py) | 20-turn adaptive attack | Social engineering detection | GPT-4o | **Detected at Turn 6. 27/30 blind evaluation.** |
| Hallucination Prevention | 5 fabrication tests | Hallucination measurement | GPT-4o | **Zero hallucinations across all 5 tests.** |

### Memory Harness (101 abilities)

| Benchmark | Tasks | Type | Model | Primary Finding |
|-----------|-------|------|-------|-----------------|
| [State Tracking](memory-retention/) | 20-turn Vantage scenario | Implicit state changes | GPT-4o | **50% fewer stale facts served as current. Blind eval 4.1/5 vs 3.5/5.** |
| [Perceptual Detection](perception-hard/) | 15-turn Morgan scenario | Signal detection in coaching | GPT-4o | **3x signal detection rate. 43% vs 14%.** |
| [Selective Metrics](perception-hard/) | 10-turn Casey scenario | Perception + reframing | GPT-4o | **Earlier detection (1 turn) on 2 of 5 signals.** |

**Total: 250 single-turn reasoning tasks + 50 interactive reasoning steps + 28 competitive programming tasks + 10 scientific computing tasks + 40 sycophancy scenarios + 20-turn adversarial attacks + 5 hallucination tests + 45 memory turns across eight benchmark suites.**

---

## How It Was Tested

All benchmarks follow a consistent protocol adapted to each product layer:

1. **Agent-native execution.** Agents called Ejentum's production Logic API themselves via tool use. The agent summarized the task, called the endpoint, received the injection, and applied it before reasoning. This mirrors real deployment: the retrieval variance is real, not simulated.

2. **Blind evaluation.** For reasoning and memory benchmarks: a separate evaluator scored outputs without knowing which condition was augmented. Generation and evaluation are separate stages. For code benchmarks: exact-match pass/fail on test cases.

3. **Cross-model validation.** Anti-deception and memory benchmarks were tested on GPT-4o, validating that the mechanism works across model families.

4. **Negative findings reported.** Correctness dips, domain regressions, and unexpected results are in the reports. We do not omit results that challenge the thesis.

---

## Key Terms

| Term | Definition |
|------|-----------|
| **Logic API** | Ejentum's REST endpoint (`POST /logicv1/`). Retrieves engineered cognitive operations from 679 abilities across four product layers. |
| **Injection** | A structured cognitive payload containing a negative gate (failure pattern to avoid), reasoning topology (execution structure), suppression signals (failure modes to block), amplification signals (patterns to prioritize), and a falsification test (verification criterion). |
| **Harness** | A product layer (Reasoning, Code, Anti-Deception, Memory). Each harness is a curated collection of abilities targeting a specific class of AI failure. |
| **Ability** | One engineered cognitive operation. The atomic unit retrieved from the database. |
| **Suppression** | Named failure modes injected as constraints. Suppression signals reduce the probability of specific reasoning shortcuts. In testing, suppression produces larger behavioral effects than amplification alone. |

**API modes:** `reasoning`, `reasoning-multi`, `code`, `code-multi`, `anti-deception`, `memory`, `memory-multi`

---

## Headline Results

### Reasoning Harness. Quality Lift (7-factor composite)

| Benchmark | Baseline | Best Condition | Delta |
|-----------|----------|---------------|-------|
| EjBench (180 tasks) | 0.621 | 0.722 | **+10.1pp** |
| BBH/CausalBench/MuSR (70 tasks) | 0.476 | 0.684 | **+20.8pp** |

### Code Harness. Correctness

| Benchmark | Baseline | With Injection | Delta |
|-----------|----------|---------------|-------|
| LiveCodeBench Hard (28 tasks) | 85.7% | **100.0%** | **+14.3pp** |
| SciCode (10 tasks) | 7 bugs | **0 bugs** | **-100%** |

### Anti-Deception Harness. Protection

| Metric | Result |
|--------|--------|
| ELEPHANT composite sycophancy | **5.8%** |
| Social engineering detection | **Turn 6 of 20** |
| Hallucinations (5 tests) | **0** |

### Memory Harness. Accuracy

| Metric | Baseline | With Injection | Delta |
|--------|----------|---------------|-------|
| Stale facts served | 1.6 | 0.8 | **-50%** |
| Perceptual detection rate | 14% | 43% | **3x** |
| Blind evaluation score | 3.5/5 | 4.1/5 | **+17%** |

### ARC-AGI-3 Process Metrics

| Metric | Baseline | Augmented |
|--------|----------|-----------|
| Memory decay slope | -0.005 (degrading) | +0.014 (improving) |
| Injection half-life | 0 | 24 steps |
| Reasoning depth trend | 0.86 | 10.50 (12.2x) |

---

## Negative Findings

- **Correctness dipped under reasoning-multi on EjBench** (-0.11 on 3-point scale). Thorougher reasoning occasionally trades accuracy for caution.
- **Spatial domain regressed under reasoning-multi on BBH** (-20.0pp on 5 tasks). Multi-perspective injection confused spatial constraint tracking.
- **Reasoning-multi correctness dropped on BBH** (-0.12). Focused tasks need focused injections. Single mode outperformed multi on every single-domain task.
- **Contradiction rate increased 1.9x on ARC-AGI-3** (token-normalized). Whether this is productive cognitive conflict or destructive interference is unresolved.
- **ARC-AGI-3: RHAE 0.0 = 0.0.** Neither condition cleared Level 0. All process metrics are measured in a failure context.

---

## What Would Falsify This

The core claim is that structured cognitive injection produces measurable behavioral changes in LLM outputs. This claim is falsified if:

1. The same injection format produces zero behavioral change on a different model family. (Partially addressed: anti-deception and memory validated on GPT-4o.)
2. Random injection (shuffled suppression signals, mismatched topologies) produces equivalent lift, meaning the specific cognitive operation doesn't matter.
3. The 7-factor rubric scoring shows evaluator bias that systematically inflates injected conditions.
4. Replication on a second independent run produces directionally different results.

---

## Limitations

- **Reasoning benchmarks are Claude-only.** Anti-deception and memory are cross-model (GPT-4o). Full cross-model reasoning testing is in progress.
- **LLM-as-judge.** Two-stage blind protocol mitigates but does not eliminate the possibility of systematic bias. Human evaluation on a subset would strengthen the evidence.
- **Custom task design bias.** EjBench tasks were designed by Ejentum. The BBH/CausalBench/MuSR benchmark addresses this with externally designed tasks.
- **Small samples on sub-analyses.** Spatial navigation regression rests on 5 tasks. ARC-AGI-3 is n=1 per condition.

---

## Repository Structure

```
benchmarks/
  README.md
  LICENSE
  ejbench/                      # 180 custom professional reasoning tasks
  bbh-causalbench-musr/         # 70 published academic reasoning tasks
  arc-agi-3/                    # Interactive multi-step reasoning (25 steps)
  lcb-hard/                     # 28 hard competitive programming tasks
  coding-benchmark/             # SciCode: 10 hard scientific computing problems
  elephant/                     # ELEPHANT sycophancy benchmark (40 scenarios)
  memory-retention/             # 20-turn implicit state change tracking
  perception-hard/              # Perceptual signal detection (Morgan + Casey)
  research/
    COGNITIVE_SCAFFOLDING_THESIS.md
    VALIDATED_CLAIMS.md
    paper/under_pressure.pdf
```

---

## Links

- **Product:** [ejentum.com](https://ejentum.com)
- **Documentation:** [ejentum.com/docs](https://ejentum.com/docs)
- **Product layers:** [Reasoning](https://ejentum.com/docs/reasoning_harness) · [Code](https://ejentum.com/docs/code_harness) · [Anti-Deception](https://ejentum.com/docs/anti_deception) · [Memory](https://ejentum.com/docs/memory_harness)
- **Skill files:** [Ejentum (all modes)](https://ejentum.com/docs/skill_unified) · [Reasoning](https://ejentum.com/docs/skill_reasoning) · [Code](https://ejentum.com/docs/skill_code) · [Anti-Deception](https://ejentum.com/docs/skill_anti_deception) · [Memory](https://ejentum.com/docs/skill_memory)
- **Blog:** [ejentum.com/blog](https://ejentum.com/blog)
- **49 benchmark tasks with outputs:** [ejentum.com/use-cases](https://ejentum.com/use-cases)
- **Integration examples:** [github.com/ejentum/examples](https://github.com/ejentum/examples)
- **MCP server (Claude Code, Cursor, Cline, Windsurf, Continue):** [github.com/ejentum/ejentum-mcp](https://github.com/ejentum/ejentum-mcp)

---

## License

Released under [CC BY 4.0](LICENSE). Share and adapt with attribution.
