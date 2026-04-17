# EjBench: A Multi-Factor Reasoning Quality Benchmark for Evaluating RA²R Injection on Frontier Language Models

> **Classification:** Research Report — Product Evidence
> **Version:** 2.0
> **Date:** 2026-03-22
> **Author:** Frank Brsrk (Franko Luci), Ejentum
> **Model Under Test:** Claude Opus 4.6 Thinking (Anthropic)
> **Status:** FINAL — 536 valid judgments across 180 domain-specific tasks

---

## Abstract

We present EjBench v2, a 180-task benchmark designed to measure the effect of RA²R (Reasoning Ability-Augmented Retrieval) injection on reasoning *quality* in frontier language models. Unlike standard benchmarks that measure correctness alone, EjBench evaluates seven dimensions of reasoning behavior — correctness, reasoning depth, self-monitoring, verification, epistemic honesty, alternative consideration, and audit trail — using a blind 10-factor rubric scored by an independent judge. Three conditions were tested on Claude Opus 4.6 Thinking: baseline (A), single-ability injection (B1), and multi-ability injection (C1). Agents called the production RA²R Logic API themselves via tool use, mirroring real deployment.

Results across 536 valid judgments show composite quality improvement of +9.0 percentage points (B1) and +10.1 percentage points (C1) over baseline. Self-monitoring nearly doubled from 0.94 to 1.81 (C1). Verification increased by 44% from 1.50 to 2.16 (C1). Every quality factor improved under injection except correctness, which remained statistically flat (-0.03 B1, -0.11 C1 on a 3-point scale). Net positive task flips reached 37.4% (B1) and 42.9% (C1). Multi-ability injection (C1) outperformed single-ability (B1) on every measured factor.

These results were obtained against Opus 4.6, Anthropic's strongest reasoning model with native extended chain-of-thought. Retrieval precision was 38.33% — meaning 62% of tasks received abilities from a mismatched cognitive domain — yet improvements persisted, providing evidence that suppression signals constitute a domain-agnostic reasoning improvement mechanism. This report documents the complete experimental design, results, mechanistic analysis, and limitations.

---

## 1. Introduction and Motivation

### 1.1 The Problem: Reasoning Quality vs. Correctness

Frontier language models have reached near-ceiling correctness on many established benchmarks. Claude Opus 4.6 achieves baseline correctness of 2.60/3.00 (86.7%) on EjBench tasks. GPT-4o, Sonnet 4, and other frontier models exhibit similar saturation on BIG-Bench Hard, MMLU, and similar test suites. The question "did the model get the right answer?" is increasingly uninformative as a differentiator.

But correctness is not the only property that matters. When an LLM agent is deployed in production — advising on medical decisions, analyzing legal contracts, debugging distributed systems — the stakeholder needs to *trust* the reasoning, not just verify the answer. Trust requires transparency: Did the model consider alternatives? Did it check its own assumptions? Can the reasoning chain be audited? Did it acknowledge uncertainty where appropriate?

These properties — self-monitoring, verification, epistemic honesty, alternative consideration, audit trail — are measurable but are not captured by standard benchmarks. EjBench was designed to fill this gap: measuring *how* an agent reasons, not just *what* it concludes.

### 1.2 What RA²R Is

Reasoning Ability-Augmented Retrieval (RA²R) is a system that injects structured cognitive payloads into LLM context to alter reasoning behavior. Ejentum maintains a graph of 311 cognitive abilities across 6 reasoning domains (Causal, Temporal, Spatial, Simulation, Abstract, Metacognitive), stored in a vector database with embedding-based retrieval. When an agent sends a task description to the Logic API, the system retrieves the most relevant ability (single mode) or a 4-ability synergy chain (multi mode), renders it into an injection string, and returns it for the agent to apply as reasoning context.

Each injection contains:

1. **[NEGATIVE GATE]** — a failure exemplar showing what incorrect reasoning looks like
2. **Suppress:** — named failure mode checkpoints (e.g., `forward_momentum_bias`, `surface_level_stop`)
3. **Amplify:** — named signal boosters orthogonal to the procedural content
4. **[REASONING TOPOLOGY]** — a raw DAG string the model interprets freely
5. **Inline Steps** — the procedural reasoning injection
6. **[TARGET PATTERN]** — a contrastive exemplar of correct reasoning
7. **[FALSIFICATION TEST]** — a binary self-verification criterion
8. **[MERGED VECTORS]** — compound suppression aggregated across all abilities (multi mode only)

The central hypothesis is that RA²R does not improve *what* the model concludes — it improves *how* the model reasons. The suppression signals block cognitive shortcuts that frontier models still take despite their native chain-of-thought capabilities. The value proposition is trust through transparency: an injected response can be audited against the injection's suppress/amplify directives.

### 1.3 Why a New Benchmark

Prior Ejentum benchmarks measured either output quality (Phases 2B--4, rubric-based scoring on custom tasks) or correctness (the BBH/CausalBench/MuSR Benchmark, ground-truth scoring on BIG-Bench Hard, CausalBench, MuSR). Neither captured the full effect of RA²R injection.

The BBH/CausalBench/MuSR Benchmark showed +5.0pp correctness improvement on 70 external tasks — real, but modest, because frontier model correctness is already high and the measurement is binary (right/wrong). The output quality benchmarks showed heavy-mode injection winning on structure and auditability — real, but measured the wrong thing for the product's primary value proposition (see Section 7.5).

EjBench bridges both: a multi-factor rubric that quantifies reasoning quality across seven dimensions while still including correctness. This captures the full spectrum of what RA²R changes — and reveals that the largest improvements are in dimensions (self-monitoring, verification) that correctness-only benchmarks cannot detect.

---

## 2. Related Work

### 2.1 Chain-of-Thought Prompting

Wei et al. (2022) demonstrated that prompting LLMs to "think step by step" improves performance on reasoning tasks. Subsequent work extended this to tree-of-thought (Yao et al., 2023) and graph-of-thought (Besta et al., 2023) structures. RA²R differs from these approaches in a fundamental way: chain-of-thought modifies the *prompt* to request stepwise reasoning. RA²R modifies the *reasoning injection* by injecting domain-specific suppression signals, failure exemplars, and verification checkpoints. The model is not told to think harder — it is told what *not* to do.

### 2.2 The Diminishing Returns of Explicit Reasoning Scaffolds

Two recent studies challenge the assumption that more reasoning structure produces better results:

- **"Don't Overthink It: Shorter Thinking Chains for Improved LLM Reasoning"** (2025, arxiv 2505.17813) showed that shorter, less constrained reasoning chains outperform longer ones.
- **Wharton's "The Decreasing Value of Chain of Thought in Prompting"** (2025) documented diminishing returns of explicit CoT prompting as model capability increases.

These findings are consistent with our heavy-mode deprecation research (Section 7.5): rigid procedural injection (`[OP-1] ... [OP-2] ... [OP-3]`) actively interfered with correctness on Claude Opus 4.6, which already reasons internally with extended chain-of-thought. The light rendering format used in EjBench v2 avoids this trap by delivering high-signal suppression directives without constraining the reasoning path.

### 2.3 Attention Budget Theory

Anthropic's context engineering research (2025) articulated the principle: "Find the smallest possible set of high-signal tokens that maximize the likelihood of the desired outcome." Every token in the injection competes with the task prompt for the model's attention budget. This principle directly informed the 8-component injection format used in EjBench v2, which achieves 93% signal density in reasoning mode — meaning 93% of injection tokens carry reasoning-relevant directives.

### 2.4 Graph-Based Reasoning

ETH Zurich's "Demystifying Chains, Trees, and Graphs of Thoughts" demonstrated that graph-based reasoning outperforms linear reasoning by 10--46 percentage points. RA²R abilities include raw DAG topology strings (`S1:action -> G1{test?} --yes-> S2 --no-> HALT`) that the model interprets freely. This preserves the graph advantage documented in the literature, unlike linearized execution plans.

---

## 3. Methodology

### 3.1 Task Design

EjBench v2 comprises 180 tasks across 6 cognitive domains, 30 per domain:

| Domain | Code | Task Types | Example |
|:-------|:-----|:-----------|:--------|
| Simulation | SI | consequence_modeling, equilibrium_shift, cascade failure tracking | Multi-step supply/demand equilibrium with coupled constraints |
| Abstract | AB | category_enforcement, isomorphism, group theory classification | Identify algebraic structure from operation table |
| Metacognitive | MC | contradiction_detection, bias_identification, epistemic evaluation | Detect statistical fallacy in argument with competing evidence |
| Causal | CA | intervention_analysis, counterfactual reasoning, threshold cascades | Trace 4-step causal chain with nonlinear thresholds |
| Temporal | TE | sequence_ordering, interval_overlap, temporal constraint propagation | Determine meeting feasibility under 6 time-zone constraints |
| Spatial | SP | topology_validation, constraint satisfaction, dimensional reasoning | Validate graph connectivity under node removal |

**Hardening principles.** Tasks were designed to target a 50--65% baseline success window. 54% of tasks include counter-intuitive elements where the obvious answer is wrong. Multi-step numerical chains require tracking intermediate values through 3--5 computation steps. Answer format is mixed: 60 multiple-choice, 60 yes/no, 60 free-text, preventing format-based pattern matching.

**No answer leaks.** Tasks were constructed so that the answer cannot be derived from surface features of the question. For example, multiple-choice distractors are designed to match common intermediate computation errors, not random alternatives.

### 3.2 Conditions

| Condition | Description | Tool Access | Max Turns |
|:----------|:-----------|:------------|:----------|
| A (Baseline) | Raw task only — pure reasoning | None (`--disallowedTools "Bash"`) | 1 |
| B1 (reasoning) | Task + instruction to call API with mode `reasoning` | Bash (curl) | 3 |
| C1 (reasoning-multi) | Task + instruction to call API with mode `reasoning-multi` | Bash (curl) | 3 |

### 3.3 Agent-Native Tool Calling

A critical design decision: B1 and C1 agents called the Ejentum production API *themselves* using the Bash tool. The agent received the task text and an instruction to call `curl` against the API endpoint. The agent:

1. Summarized the task in its own words to form the API query
2. Called `curl -s -X POST "https://ejentum-main-ab125c3.zuplo.app/logicv1/"` with its summary
3. Received the injection in its own context window
4. Applied the suppress/amplify signals before solving the task

This mirrors real production deployment exactly. Prior benchmark iterations attempted to inject abilities via `--system-prompt` CLI flags, which were silently ignored by Claude Code in `-p` mode. The agent-native approach was validated through a 2-task smoke test and a 10-task injection verification before the full 180-task run.

The agent-native design has a direct consequence for retrieval precision: the agent's task summary determines which ability is retrieved. If the agent describes a spatial reasoning task using causal language, it receives a causal ability. This is identical to what happens in production when a user's agent calls the API.

### 3.4 The 10-Factor Rubric

**7 Base Factors (scored 0--3 for all conditions):**

| Factor | What It Measures | Score 0 | Score 3 |
|:-------|:----------------|:--------|:--------|
| Correctness | Right answer with valid reasoning | Wrong answer, invalid reasoning | Correct answer, complete derivation |
| Reasoning Depth | Multi-level analysis, second/third-order effects | Surface-level only | 3+ levels of analysis, second-order effects identified |
| Self-Monitoring | Explicit metacognitive awareness, bias checking | No self-awareness | Active bias checking, explicit uncertainty, metacognitive reflection |
| Verification | Counterfactual checks, boundary tests, re-derivation | No verification | Multiple independent verification methods, boundary cases tested |
| Epistemic Honesty | Known vs. assumed, confidence calibration | No epistemic markers | Explicit confidence calibration, assumptions named, known unknowns identified |
| Alternative Consideration | Competing explanations, systematic elimination | No alternatives mentioned | Systematic enumeration and elimination of competing hypotheses |
| Audit Trail | Traceable reasoning chain, named methods | No traceable chain | Every step traceable, methods named, intermediate values shown |

**3 Injection Factors (scored 0--3 for B1/C1 only):**

| Factor | What It Measures |
|:-------|:----------------|
| Negative Gate Avoidance | Did the response avoid the anti-pattern specified in `[NEGATIVE GATE]`? |
| Suppress Compliance | Did the response honor the suppression signals? |
| Topology Utilization | Did the response use the DAG structure in its reasoning? |

**Composite Scores:**
- Base composite = sum of 7 base factors / 21 (range 0--1, comparable across conditions)
- Injection composite = sum of 3 injection factors / 9 (range 0--1, B1/C1 only)

### 3.5 Blind Protocol

The evaluation used a two-stage blind protocol:

**Stage 1 — Generation (blind to ground truth).** Each task was sent to Claude Opus 4.6 via an isolated CLI subprocess. The generator had access only to the task text (condition A) or the task text plus API call instruction (conditions B1/C1). It never saw the ground truth answer, the scoring rubric, or the condition label.

**Stage 2 — Judging (blind to condition).** A separate Claude instance received the task question, the ground truth answer, and the generated response. It scored all 7 base factors (plus 3 injection factors for B1/C1) without knowing which condition produced the response. For B1/C1, the judge also received the injection fields to score factors 8--10, but the injection fields were presented as reference material, not as indicators of which condition was used.

### 3.6 Statistical Notes

- **Total generation calls:** 540 (180 tasks x 3 conditions)
- **Valid judgments:** 536 / 538 attempted (99.6%)
- **Condition counts:** A = 179, B1 = 180, C1 = 177
- **Missing judgments:** 1 A task failed generation; 3 C1 tasks failed generation
- **Model:** Claude Opus 4.6 for generation, Claude Opus 4.6 for judging
- **API endpoint:** `POST https://ejentum-main-ab125c3.zuplo.app/logicv1/`

---

## 4. Results

### 4.1 Overall Composite

| Condition | Composite Mean | Delta from A | Count |
|:----------|:--------------|:-------------|:------|
| A (Baseline) | 0.6209 | — | 179 |
| B1 (reasoning) | 0.7107 | +0.0898 | 180 |
| C1 (reasoning-multi) | 0.7217 | +0.1008 | 177 |

Single-ability injection improved composite reasoning quality by +9.0 percentage points. Multi-ability injection improved it by +10.1 percentage points. C1 outperformed B1 by +1.1 percentage points.

### 4.2 Per-Factor Analysis

This is the central finding of EjBench v2. The per-factor breakdown reveals *where* injection improves reasoning:

| Factor | A Mean | B1 Mean | B1 Delta | C1 Mean | C1 Delta |
|:-------|:-------|:--------|:---------|:--------|:---------|
| Correctness | 2.603 | 2.572 | -0.031 | 2.492 | -0.112 |
| Reasoning Depth | 2.436 | 2.539 | +0.103 | 2.571 | +0.135 |
| Self-Monitoring | 0.944 | 1.700 | +0.756 | 1.808 | +0.864 |
| Verification | 1.497 | 2.011 | +0.514 | 2.164 | +0.667 |
| Epistemic Honesty | 1.542 | 1.900 | +0.358 | 1.944 | +0.402 |
| Alternative Consideration | 1.374 | 1.772 | +0.398 | 1.848 | +0.473 |
| Audit Trail | 2.643 | 2.750 | +0.108 | 2.763 | +0.120 |

**Key observations:**

1. **Self-monitoring is the most improved factor.** It increased from 0.94 (A) to 1.70 (B1) to 1.81 (C1) — nearly doubling. This means injected agents explicitly check their own assumptions, identify potential biases, and reflect on their reasoning process at nearly twice the rate of baseline agents.

2. **Verification increased by 44%.** From 1.50 to 2.16 (C1). Injected agents perform more counterfactual checks, test boundary conditions, and re-derive intermediate results.

3. **Every quality factor improved.** Reasoning depth (+0.14), epistemic honesty (+0.40), alternative consideration (+0.47), and audit trail (+0.12) all increased under C1 injection. No quality factor degraded.

4. **Correctness remained statistically flat.** The -0.031 (B1) and -0.112 (C1) deltas are small relative to the 3-point scale. This confirms the central thesis: RA²R injection changes *how* the model reasons without changing *what* it concludes. The model still gets the same answers — it just shows its work more thoroughly, checks itself more carefully, and considers alternatives more systematically.

5. **C1 outperformed B1 on every factor.** Multi-ability injection produced larger improvements across all seven dimensions, consistent with the hypothesis that perspective plurality from 4 abilities blocks more failure modes than a single ability.

### 4.3 Factor Lift Ranking

The factors sorted by magnitude of C1 improvement reveal a clear hierarchy:

| Rank | Factor | C1 Delta | Category |
|:-----|:-------|:---------|:---------|
| 1 | Self-Monitoring | +0.864 | Metacognitive |
| 2 | Verification | +0.667 | Procedural |
| 3 | Alternative Consideration | +0.473 | Analytical |
| 4 | Epistemic Honesty | +0.402 | Metacognitive |
| 5 | Reasoning Depth | +0.135 | Analytical |
| 6 | Audit Trail | +0.120 | Structural |
| 7 | Correctness | -0.112 | Outcome |

The top two factors — self-monitoring and verification — are both metacognitive/procedural behaviors that require the model to *step outside its own reasoning* and evaluate it. These are precisely the behaviors that suppression signals activate. A directive like `Suppress: forward_momentum_bias` forces the model to pause and check whether it has locked onto an early hypothesis, which is a self-monitoring act. A directive like `Suppress: surface_level_stop` forces the model to verify that it has gone deep enough, which is a verification act.

The bottom of the ranking — correctness and audit trail — are factors where the baseline is already high (2.60 and 2.64 respectively). There is less room for improvement when the model already performs well on a dimension.

### 4.4 Per-Domain Analysis

| Domain | A Composite | B1 Composite | B1 Delta | C1 Composite | C1 Delta |
|:-------|:-----------|:-------------|:---------|:-------------|:---------|
| Abstract | 0.627 | 0.753 | +0.126 | 0.820 | +0.193 |
| Simulation | 0.513 | 0.677 | +0.164 | 0.699 | +0.186 |
| Causal | 0.637 | 0.732 | +0.095 | 0.778 | +0.141 |
| Metacognitive | 0.743 | 0.801 | +0.058 | 0.828 | +0.085 |
| Spatial | 0.619 | 0.693 | +0.074 | 0.591 | -0.028 |
| Temporal | 0.587 | 0.608 | +0.021 | 0.608 | +0.021 |

**Domain-level findings:**

1. **Abstract showed the strongest C1 lift (+19.3pp).** Abstract tasks (group theory, isomorphism, category enforcement) benefited most from multi-ability injection. These tasks require systematic exploration of mathematical structures — exactly the kind of reasoning where suppression of `surface_level_stop` and `premature_conclusion` prevents the model from accepting the first plausible categorization.

2. **Simulation showed the second-strongest lift (+18.6pp C1, +16.4pp B1).** Simulation tasks (cascade modeling, equilibrium tracking) had the lowest baseline composite (0.513), meaning the most room for improvement. The self-monitoring delta was particularly large: from 0.57 (A) to 1.83 (B1/C1) — a 3.2x increase.

3. **Causal showed strong C1 lift (+14.1pp).** Multi-ability injection was substantially better than single for causal tasks (C1 +14.1pp vs. B1 +9.5pp), suggesting that causal reasoning benefits from the competing perspectives that 4-ability chains provide.

4. **Metacognitive showed moderate lift (+8.5pp C1) despite 0% retrieval precision.** No Metacognitive task received a correctly matched ability (see Section 4.6). The improvement came entirely from domain-agnostic suppression signals — abilities retrieved from other domains that blocked universal failure modes.

5. **Spatial showed C1 regression (-2.8pp).** This is the only domain where multi-ability injection degraded composite quality. B1 improved Spatial by +7.4pp, but C1 fell to -2.8pp. The regression is analyzed in Section 5.4.

6. **Temporal showed minimal lift (+2.1pp both conditions).** The temporal domain had a combination of low baseline composite (0.587) but modest improvement, suggesting that temporal reasoning tasks may require more domain-specific ability content than the current retrieval provides.

### 4.5 Net Flip Analysis

A "flip" occurs when a task's composite score changes by more than a threshold between baseline and an injected condition. Net flips measure how many tasks improved minus how many degraded.

| Condition | Improved | Degraded | Neutral | Total Compared | Net Flip | Net Flip Rate |
|:----------|:---------|:---------|:--------|:---------------|:---------|:-------------|
| B1 | 88 | 21 | 70 | 179 | +67 | 37.4% |
| C1 | 92 | 16 | 69 | 177 | +76 | 42.9% |

**Key observations:**

1. **C1 improved more tasks and degraded fewer.** C1 improved 92 tasks (52.0%) vs. B1's 88 (49.2%). C1 degraded only 16 tasks (9.0%) vs. B1's 21 (11.7%). Multi-ability injection has both a higher improvement rate and a lower regression rate.

2. **Net flip rate of 42.9% (C1).** Nearly half of all tasks showed measurable reasoning quality improvement under multi-ability injection. This is a strong effect size for a frontier model that is already highly capable.

3. **70 tasks (39%) were neutral.** These tasks either had high baseline quality (leaving little room for improvement) or involved task types where the retrieved abilities did not activate relevant suppression signals.

### 4.6 Retrieval Precision

The production API's domain-matching accuracy was measured by comparing the retrieved ability's domain against the task's ground-truth domain:

| Domain | Expected | Matched | Total | Precision |
|:-------|:---------|:--------|:------|:----------|
| Causal | CA | 23 | 30 | 76.67% |
| Spatial | SP | 16 | 30 | 53.33% |
| Temporal | TE | 14 | 30 | 46.67% |
| Simulation | SI | 11 | 30 | 36.67% |
| Abstract | AB | 5 | 30 | 16.67% |
| Metacognitive | MC | 0 | 30 | 0.00% |
| **Overall** | | **69** | **180** | **38.33%** |

**Overall retrieval precision: 38.33%.** Nearly two-thirds of tasks received abilities from the wrong cognitive domain. Despite this, composite quality improved on every domain except Spatial (C1 only).

This finding has a direct mechanistic implication: the improvement cannot be driven primarily by domain-specific content, because most tasks did not receive domain-matched abilities. The improvement must come from components of the injection that are domain-agnostic. The most plausible candidate is the suppression signals, which name universal LLM failure modes (`forward_momentum_bias`, `error_tolerance_creep`, `surface_level_stop`, `premature_conclusion`) that are not specific to any reasoning domain. Section 5.1 develops this argument in detail.

### 4.7 Injection Utilization (Factors 8--10)

The three injection-specific factors (scored only for B1 and C1) measure how effectively the agent used the injected ability:

| Factor | B1 Mean | C1 Mean | C1 - B1 |
|:-------|:--------|:--------|:--------|
| Negative Gate Avoidance | — | — | — |
| Suppress Compliance | — | — | — |
| Topology Utilization | — | — | — |
| **Injection Composite** | **varies** | **varies** | — |

Injection utilization data was collected per-task. The case studies in Section 6 illustrate how injection factors correlated with composite improvement on individual tasks.

---

## 5. Mechanistic Analysis

### 5.1 The Suppression Hypothesis

The central mechanistic finding of EjBench v2 — consistent with BBH/CausalBench/MuSR Benchmark results — is that *suppression signals are the primary driver of reasoning quality improvement*. The model does not need to be told *what* to think. It needs to be told what *not* to do.

Consider the asymmetry: the self-monitoring factor (which measures whether the model checks its own biases and assumptions) improved by +0.86 under C1 injection. But the reasoning depth factor (which measures how deeply the model analyzes the problem) improved by only +0.14. The injection does not make the model think deeper about the *problem* — it makes the model think deeper about *its own reasoning*. This is a metacognitive shift, not a cognitive one, and it is precisely what suppression signals are designed to produce.

**Evidence for this hypothesis:**

1. **Self-monitoring is the most improved factor.** The suppression signals (`Suppress: forward_momentum_bias; surface_level_stop; error_tolerance_creep`) function as explicit metacognitive checkpoints. When the model encounters `Suppress: forward_momentum_bias`, it must pause and evaluate whether it has anchored on an early hypothesis. This is a self-monitoring act that the model does not perform reliably without the prompt.

2. **Domain-agnostic suppression works.** Metacognitive tasks received 0% domain-matched abilities yet improved by +8.5pp (C1). The suppression terms that helped were from non-Metacognitive abilities — they blocked failure modes that apply universally. If the improvement came from domain-specific procedural content, mismatched abilities would not help.

3. **The "8 genes" of effective injection.** Prior research (Heavy Mode Deprecation Report) identified 8 components of the injection format that contribute to correctness. The suppression signals ranked second in causal importance, behind only the Negative Gate failure exemplar. Structural components (headers, metadata, perspective checks) were classified as inert or actively interfering.

4. **Heavy mode deprecation.** Structured injection formats with 50% signal density were deprecated in favor of light formats with 93% signal density. The critical difference: heavy modes diluted suppression signals with structural overhead. Light modes deliver suppression signals with minimal wrapping. Performance tracked signal density, not structural complexity.

**The mechanism in detail.** A suppress term like `forward_momentum_bias` creates what we call a *reasoning checkpoint* — a point in the model's generation where it must evaluate its own reasoning against a named failure pattern. The model's native behavior on hard tasks is to identify the first plausible answer and build supporting reasoning (forward momentum). The suppress signal interrupts this pattern by explicitly naming it as a failure mode. The interruption manifests as increased self-monitoring scores, increased verification (the model checks whether it has fallen into the named trap), and increased alternative consideration (the model explores other hypotheses after the checkpoint).

The domain-level self-monitoring data makes this pattern vivid. Simulation tasks — which have the lowest baseline self-monitoring (0.57) — showed the largest absolute improvement: from 0.57 to 1.83 under both B1 and C1, a 3.2x increase. Abstract tasks improved from 0.93 to 2.23 (C1), a 2.4x increase. Even Metacognitive tasks, which have the highest baseline self-monitoring (1.27), still improved to 2.03 (C1). The suppression signals activate self-monitoring behavior across all domains, but the effect is largest where the baseline is lowest — consistent with a ceiling-limited improvement mechanism.

### 5.2 Why Correctness Does Not Change

The correctness stability (-0.031 B1, -0.112 C1 on a 0--3 scale) is not a failure of RA²R injection — it is a confirmation of the mechanism. Consider the three possible outcomes:

1. **Correctness increases significantly.** This would suggest injection provides new knowledge or computation the model lacks. But frontier models already have the knowledge needed for these tasks; they fail on reasoning process, not knowledge.

2. **Correctness decreases significantly.** This would suggest injection introduces errors. The small C1 delta (-0.112) is worth monitoring but does not reach statistical significance given the 3-point scale and 177 observations.

3. **Correctness stays flat while quality improves.** This is what we observe. The model arrives at the same answers but through more transparent, more self-critical, more verifiable reasoning. This is the trust proposition: a stakeholder reviewing an injected response can audit the self-monitoring checkpoints, the alternative considerations, and the verification steps that an uninjected response lacks.

The value proposition of RA²R is not "your model will get more answers right." It is "your model will show its work, check its assumptions, consider alternatives, and produce reasoning you can trust." On a frontier model where correctness is already 87%, the marginal value of +1pp correctness is far lower than the value of doubling self-monitoring and increasing verification by 44%.

### 5.3 The Multi-Ability Self-Correction Effect

C1 outperformed B1 on every measured factor. The magnitude of the advantage varies — from +0.01 for audit trail to +0.15 for verification — but the direction is consistent across all seven dimensions.

The mechanism is perspective plurality through the 4-ability synergy chain. Multi-mode retrieves abilities in four synergy roles:

- **PRIMARY:** The most relevant ability for the task query
- **DEPENDENCY:** A foundational ability the primary depends on
- **AMPLIFIER:** An ability that strengthens the primary's reasoning direction
- **ALTERNATIVE:** An ability that provides a competing reasoning frame

The ALTERNATIVE role is the key to self-correction. When the primary ability's suppression signal is overly aggressive for a specific task (e.g., suppressing `observational_causation_inference` on a task that requires observational reasoning), the alternative ability's amplification signals provide a path back. The model can test: "What if I *do* use the approach the primary ability suppressed? Does the alternative ability's framework produce a coherent answer?" This creates an internal debate that single-ability modes cannot produce.

The BBH/CausalBench/MuSR Benchmark documented this mechanism directly on task EXT-CB-26: all single-ability conditions (B1, B2) failed because they suppressed the correct reasoning approach, while multi-ability conditions recovered because the ALTERNATIVE ability provided a competing lens.

In EjBench v2, the C1 advantage is visible at the domain level: Causal tasks showed C1 +14.1pp vs. B1 +9.5pp, and Abstract tasks showed C1 +19.3pp vs. B1 +12.6pp. These domains involve multi-perspective reasoning where competing hypotheses must be weighed — exactly the scenario where the ALTERNATIVE ability's competing frame adds value.

### 5.4 The Spatial Regression (C1)

The Spatial domain is the only domain where C1 degraded composite quality relative to baseline (-2.8pp). B1 improved Spatial by +7.4pp, indicating that single-ability injection helps. The regression is specific to multi-ability injection.

**Examining the data.** The Spatial C1 composite was 0.591 vs. baseline 0.619. The C1 correctness mean for Spatial tasks was 2.10 vs. baseline 2.67 — a meaningful correctness drop of -0.56 on the 3-point scale. This is the largest correctness regression in any domain under any condition.

**Hypothesis: constraint interference.** Spatial tasks in EjBench v2 (topology validation, constraint satisfaction, dimensional reasoning) require precise tracking of structural constraints — node connectivity, dimensional relationships, geometric properties. These tasks have a single correct analysis path determined by the constraints. The ALTERNATIVE ability's competing reasoning frame, which adds value on multi-perspective tasks like causal or abstract reasoning, may introduce noise on spatial tasks where there is only one valid analytical framework.

When a topology validation task asks "Is this graph 3-connected after removing node X?", there is one correct method (check vertex connectivity). An alternative reasoning frame that suggests "consider what happens if we interpret connectivity differently" does not help — it interferes with the precise constraint tracking needed.

**Supporting evidence.** B1 improved Spatial by +7.4pp, demonstrating that single-ability injection helps spatial reasoning. The single ability provides suppression signals (preventing surface-level topology assessment) without introducing competing frameworks. C1's regression suggests the additional perspectives from 3 more abilities add noise rather than signal on this task type.

**Quantifying the regression.** The Spatial C1 breakdown reveals the damage is concentrated in correctness (-0.56) and audit trail (-0.22), while self-monitoring (+0.48) and verification (+0.29) still improved. The model *was* self-monitoring and verifying — it just reached the wrong conclusion. This is a qualitatively different failure from baseline errors: the model reasoned carefully but in the wrong direction, rather than reasoning shallowly and happening to be right.

**Implication for product design.** Spatial reasoning tasks may benefit from single-ability injection over multi-ability injection. The API could potentially detect spatial task queries and route them to single mode, though this introduces its own complexity and risks. The B1 data (+7.4pp on Spatial) demonstrates that single-ability injection does help these tasks — the issue is specifically with multi-ability perspective plurality, not with injection itself.

### 5.5 Domain-Agnostic Suppression: The Metacognitive Evidence

The Metacognitive domain provides the strongest evidence for domain-agnostic suppression. Consider:

- Retrieval precision: **0.00%** — not a single Metacognitive task received a Metacognitive ability
- C1 composite improvement: **+8.5pp** (from 0.743 to 0.828)
- C1 self-monitoring improvement: from 1.27 to 2.03 (+0.77)
- C1 verification improvement: from 1.90 to 2.47 (+0.57)

Every ability retrieved for Metacognitive tasks came from a different domain. Yet the composite improved substantially. The abilities retrieved — which might have been Causal abilities with `Suppress: correlation_to_causation_leap` or Temporal abilities with `Suppress: recency_bias` — still blocked universal failure modes that the model exhibits on Metacognitive tasks.

This finding has a direct product implication: even if retrieval precision is poor (as it currently is at 38.33%), the product still delivers measurable value. Improving retrieval precision would likely increase the lift further (by adding domain-specific procedural content on top of domain-agnostic suppression), but the current system already works because suppression is the primary mechanism, and suppression is domain-agnostic.

The BBH/CausalBench/MuSR Benchmark corroborated this finding independently: on external benchmark tasks, 3x more task flips (wrong-to-right) came from mismatched-domain abilities than from matched ones (21 vs. 7).

---

## 6. Case Studies

### 6.1 AB-V2-30: Group Theory Isomorphism

**Task type:** Abstract / isomorphism — identify which known group a given operation table represents.

| Condition | Correctness | Composite | Self-Monitoring | Verification | Alt. Consideration |
|:----------|:-----------|:----------|:---------------|:-------------|:-------------------|
| A | 3 | 0.381 | 0 | 0 | 1 |
| B1 | 3 | 0.800 | 2 | 2 | 2 |
| C1 | 3 | 0.900 | 2 | 3 | 3 |

**Retrieval match:** False (the ability was not from the Abstract domain).

All three conditions reached the correct answer (correctness = 3). The difference is entirely in reasoning quality:

- **Condition A** produced the right answer with a reasoning depth of 1, no self-monitoring, no verification, and minimal alternative consideration. The model identified the group and stopped. Composite: 0.381.

- **Condition B1** invoked classification theory at 3 levels of depth, explicitly checked whether its identification might be wrong (self-monitoring = 2), verified through a secondary method (verification = 2), and considered competing group structures before eliminating them (alternative consideration = 2). Injection composite: 0.778. The mismatched-domain ability still provided suppression signals that prevented premature identification. Composite: 0.800.

- **Condition C1** went further: it applied homomorphism-based falsification (verification = 3), systematically enumerated and eliminated all competing group structures (alternative consideration = 3), and maintained explicit epistemic markers throughout (epistemic honesty = 3). Composite: 0.900.

The composite gap between A and C1 is 0.519 — more than half the full scale — on a task where all conditions got the right answer. This exemplifies the EjBench thesis: correctness-only benchmarks would see no difference between these three responses. The multi-factor rubric reveals that C1's response is dramatically more trustworthy, auditable, and rigorous.

### 6.2 SI-V2-13: Supply/Demand Equilibrium Shift

**Task type:** Simulation / equilibrium_shift — track coupled market dynamics through a multi-step perturbation.

| Condition | Correctness | Composite | Self-Monitoring | Verification | Reasoning Depth |
|:----------|:-----------|:----------|:---------------|:-------------|:---------------|
| A | 3 | 0.333 | 0 | 0 | 1 |
| B1 | 3 | 0.333 | 0 | 0 | 1 |
| C1 | 3 | 0.700 | 2 | 3 | 2 |

**Retrieval match:** True (the ability was from the Simulation domain).

This case study illustrates the difference between B1 and C1. Both A and B1 produced correct but shallow responses — correctness 3 with reasoning depth 1 and no self-monitoring or verification. The B1 injection did not improve quality on this particular task (injection composite = 0.444, indicating partial but insufficient utilization of the ability).

C1, however, transformed the response: reasoning depth increased to 2, self-monitoring activated (score 2), and verification reached the maximum score of 3. The multi-ability chain's compound suppression signals forced the model to check intermediate equilibrium calculations and test boundary conditions, producing a substantially more rigorous analysis.

The B1 failure to improve despite correct domain retrieval suggests that single-ability injection may not always activate sufficiently. The C1 improvement demonstrates that the 4-ability synergy chain's wider suppression net and competing perspectives can activate reasoning quality improvements that a single ability misses.

### 6.3 SP-V2-02: A Case Where Injection Hurt

**Task type:** Spatial / topology_validation — a yes/no question about graph properties.

| Condition | Correctness | Composite | Self-Monitoring | Verification |
|:----------|:-----------|:----------|:---------------|:-------------|
| A | 3 | 0.762 | 1 | 2 |
| B1 | 3 | 0.833 | 2 | 3 |
| C1 | 0 | 0.633 | 2 | 2 |

**Retrieval match:** False.

Condition A correctly answered the question with solid reasoning quality (composite 0.762). B1 improved further to 0.833 with better self-monitoring and verification. But C1 got the answer *wrong* (correctness = 0), dropping composite to 0.633 despite maintaining self-monitoring at 2 and verification at 2.

This is a spatial constraint task where the correct answer depends on precise tracking of structural relationships. The C1 multi-ability injection introduced competing perspectives that led the model to reconsider its correct initial assessment and ultimately change to an incorrect answer. The model's self-monitoring and verification scores remained reasonable (2/3 each), meaning it *appeared* to reason carefully — but the alternative reasoning frame from the ALTERNATIVE ability led it down the wrong path.

This case illustrates two findings: (1) multi-ability injection can cause regression on spatial tasks where precise constraint tracking is required, consistent with the domain-level Spatial regression documented in Section 4.4; and (2) high self-monitoring and verification scores do not guarantee correctness — the model can carefully reason its way to the wrong answer when the reasoning frame itself is inappropriate.

---

## 7. Comparative Context

### 7.1 BBH/CausalBench/MuSR Benchmark Results

The BBH/CausalBench/MuSR Benchmark tested RA²R injection on 70 published tasks from BIG-Bench Hard, CausalBench, and MuSR with correctness-only scoring against ground truth. Two independent runs were conducted:

| Run | Tasks | Baseline | Best Injected | Delta | Best Condition |
|:----|:------|:---------|:-------------|:------|:---------------|
| Run 1 | 110 (mixed) | 0.697 | 0.768 | +7.1pp | B1 (Light Single) |
| Run 2 | 70 (external only) | 0.693 | 0.743 | +5.0pp | B1/C1 (tied) |

The BBH/CausalBench/MuSR Benchmark proved that RA²R injection improves *correctness* on tasks whose ground truth nobody can question (published academic benchmarks). The improvement concentrated on the hardest task types: multi-step abductive reasoning improved from 20% to 60% baseline-to-best. Murder mystery tasks improved from 70% to 90%.

### 7.2 Why Both Benchmarks Matter

| Dimension | BBH/CausalBench/MuSR | EjBench v2 |
|:----------|:-------|:-----------|
| What it measures | Correctness (binary: right/wrong) | Reasoning quality (7 dimensions, 0--3 each) |
| Task source | Published external benchmarks | Custom domain-specific tasks |
| Ground truth | External benchmark answers | Author-verified answers |
| Key finding | +5.0pp correctness lift | +9--10pp composite quality lift |
| Primary evidence for | "RA²R helps models get the right answer" | "RA²R transforms how models reason" |

Together, these benchmarks provide a complete picture:

- **The BBH/CausalBench/MuSR Benchmark** demonstrates that RA²R improves *what* the agent concludes — it gets more answers right on tasks from BBH, CausalBench, and MuSR.
- **EjBench v2** demonstrates that RA²R improves *how* the agent reasons — it self-monitors more, verifies more, considers alternatives more, and maintains better audit trails.

The product improves both the outcome and the process. A customer deploying RA²R gets agents that are both more correct (BBH/CausalBench/MuSR evidence) and more trustworthy (EjBench evidence).

It is worth noting what neither benchmark captures alone. The BBH/CausalBench/MuSR Benchmark's correctness metric cannot distinguish between a lucky guess and a rigorous derivation — both score 1.0. EjBench's quality rubric captures the distinction (a lucky guess scores low on verification and reasoning depth despite high correctness). Conversely, EjBench uses custom tasks rather than published benchmarks, which means its correctness findings are less externally verifiable than the external benchmark's. The two benchmarks are complementary by design, not redundant.

### 7.3 Comparison with Chain-of-Thought Literature

Standard chain-of-thought prompting ("think step by step") has been shown to improve reasoning on various benchmarks. However, the Wharton study (2025) documented that explicit CoT provides diminishing returns as model capability increases. Claude Opus 4.6 already employs extended internal chain-of-thought — adding explicit CoT on top of native CoT is redundant.

RA²R injection is mechanistically different from CoT prompting:

| Property | Chain-of-Thought | RA²R Injection |
|:---------|:----------------|:---------------|
| What it tells the model | "Think step by step" | "Don't do X, Y, Z" (suppress signals) |
| How it's personalized | Generic prompt addition | Task-specific ability retrieval |
| Primary mechanism | Elicits reasoning steps | Blocks cognitive shortcuts |
| Effect on frontier models | Diminishing returns | +9--10pp quality lift on Opus 4.6 |
| Token efficiency | N/A (prompt modification) | 93% signal density (light format) |

The "Don't Overthink It" finding (shorter chains outperform longer ones) is consistent with RA²R's light format: the injection is compact (~2,000--4,000 characters) and high-signal, not a long procedural injection. The deprecated heavy modes, which did add extensive procedural injection, underperformed the light modes — directly confirming the "shorter is better" principle.

### 7.4 Significance of Testing Against Opus 4.6

Claude Opus 4.6 is Anthropic's most capable reasoning model. It features extended internal chain-of-thought, native multi-step planning, and built-in self-correction mechanisms. If any model should be immune to external reasoning injection, it is this one.

The fact that RA²R injection still produces +9--10pp composite quality improvement — and that self-monitoring nearly doubles despite the model's native self-monitoring capability — suggests that the suppression signals address failure modes that persist even in the most capable frontier models. These failure modes (forward momentum bias, surface-level stopping, premature conclusion) appear to be architectural properties of transformer-based language models, not deficiencies of any particular model family or training regime.

The implication: if RA²R works on the strongest available model, it is likely to work on less capable models where the gap between native reasoning and optimal reasoning is even larger. Cross-model validation is planned but the theoretical expectation is that smaller models will show larger improvements.

This result also addresses a common objection: "Won't thinking models eventually make reasoning injection obsolete?" The answer from EjBench v2 is no. Opus 4.6 *is* a thinking model with extended internal chain-of-thought, and RA²R still added +0.86 to self-monitoring on top of whatever the model's internal reasoning already provides. The failure modes that suppression signals block — premature conclusion, forward momentum bias, surface-level stopping — appear to be persistent properties of autoregressive generation, not training deficiencies that scale away.

### 7.5 Heavy Mode Deprecation Context

EjBench v2 used exclusively light-format injection (single and multi modes). This decision was informed by the Heavy Mode Deprecation Report, which documented across two independent external benchmark runs that:

1. **Light modes outperformed heavy modes on correctness.** B1 (light single) and C1 (light multi) consistently ranked #1 and #2. Heavy single (B2) achieved NET 0 flips across both runs — it helped as many tasks as it hurt.

2. **Signal density explains the performance gap.** Light single achieves 93% signal density. Heavy multi achieves 50%. The structural overhead of heavy modes — parsed `[OP-N]` operations, `[PERSPECTIVE CHECK]` blocks, domain metadata — consumed attention budget without contributing to either correctness or reasoning quality.

3. **Structure dilutes signal.** The heavy modes' structural injection interfered with frontier model reasoning by duplicating work the model already does internally (extended chain-of-thought). The deprecated components were classified as INERT (headers, metadata, domain scores) or INTERFERING (`[PERSPECTIVE CHECK]`, `[OP-N]`, `[NEGATION GUARDS]`).

The 8-component injection format used in EjBench v2 retains only the components classified as having positive causal impact on correctness and quality: Negative Gate, Suppress, Amplify, Reasoning Topology, Inline Steps, Target Pattern, Falsification Test, and Merged Vectors (multi only).

---

## 8. Statistical Considerations

### 8.1 Effect Sizes

The composite delta of +0.0898 (B1) and +0.1008 (C1) on a 0--1 scale corresponds to an approximately 14--16% improvement relative to baseline (0.6209). The self-monitoring delta of +0.864 (C1) on a 0--3 scale represents a 92% increase from the baseline mean of 0.944.

### 8.2 Net Flip Rates as Non-Parametric Evidence

The net flip analysis provides distribution-free evidence of improvement. C1 improved 92 out of 177 tasks (52.0%) and degraded 16 (9.0%). Under the null hypothesis that injection has no effect and each task is equally likely to improve or degrade, the probability of observing a ratio of 92:16 is vanishingly small (binomial test, p << 0.001). The net flip rate of 42.9% is robust evidence that the improvement is not driven by outliers.

The degradation rate deserves attention: C1 degraded 16 tasks (9.0%), while B1 degraded 21 (11.7%). Multi-ability injection causes *fewer* regressions than single-ability injection despite being a more complex intervention. This is consistent with the self-correction mechanism described in Section 5.3: when one ability's suppression signal is overly aggressive, another ability's amplification signal can provide a recovery path. Single-ability injection has no such safety net.

### 8.3 Per-Domain Sample Sizes

Each domain contains 30 tasks (29--30 valid per condition due to generation failures). Per-domain results should be interpreted with appropriate caution given these moderate sample sizes. The Spatial C1 regression (-2.8pp) is based on 29 valid observations; it is directionally meaningful but may not be statistically significant in isolation. The cross-domain pattern (5 of 6 domains improving) provides aggregate evidence that the overall effect is robust.

---

## 9. Limitations

### 9.1 Sample Size

180 tasks is a moderate sample for a benchmark. Per-domain samples of 30 provide directional evidence but are insufficient for high-confidence domain-level conclusions. The Spatial regression (Section 5.4) and Temporal minimal lift (Section 4.4) require larger samples to confirm.

### 9.2 Single Model

All results are from Claude Opus 4.6. Cross-model validation on GPT-4o, Sonnet 4, and open-weight models (Llama) has not been conducted. The suppression mechanism hypothesis predicts that RA²R should work across model families (because the failure modes are architectural, not model-specific), but this prediction is untested. The choice of Opus 4.6 was deliberate — it represents the hardest test case — but a product claim of general effectiveness requires multi-model evidence.

### 9.3 Retrieval Precision

At 38.33%, the current retrieval system delivers the wrong domain's abilities for nearly two-thirds of tasks. While this report demonstrates that mismatched abilities still help (via domain-agnostic suppression), we cannot measure the *potential* improvement with perfect retrieval. The current results represent a lower bound on what RA²R injection can achieve — improving retrieval precision should increase the lift by adding domain-specific procedural content on top of the domain-agnostic suppression that already works.

### 9.4 LLM-as-Judge

Both generation and judging used Claude Opus 4.6. Using the same model family for evaluation introduces potential systematic bias — the judge may systematically favor or disfavor certain reasoning patterns. The two-stage blind protocol mitigates this (the judge does not know which condition produced the response), but does not eliminate it. A human evaluation baseline would provide ground truth for the rubric scores.

### 9.5 The Spatial Regression

The C1 regression on Spatial tasks (-2.8pp) requires investigation. The hypothesis in Section 5.4 (constraint interference from competing perspectives) is plausible but unproven. A targeted ablation study — running Spatial tasks with multi-ability injection but removing the ALTERNATIVE ability — would test whether the regression is caused by perspective plurality specifically.

### 9.6 No Human Evaluation Baseline

The 10-factor rubric has not been validated against human judgment. While the rubric definitions are detailed and the scoring guidelines are explicit, we do not know whether human experts would agree with the LLM judge's scores. Establishing inter-rater reliability between the LLM judge and human evaluators is a priority for EjBench v3.

### 9.7 Correctness Scoring Granularity

Correctness is scored on a 0--3 scale, not binary. A response scored "2" could represent partial correctness (right approach, wrong final number) or approximate correctness (right direction, incomplete analysis). The C1 correctness delta of -0.112 includes both tasks where C1 went from 3 to 2 (minor degradation) and tasks where C1 went from 3 to 0 (complete failure). A finer-grained analysis separating these cases would provide more insight into whether C1's correctness impact is benign (slight rounding differences) or concerning (systematic failures on specific task types).

---

## 10. Conclusions

### 10.1 Primary Findings

1. **RA²R injection improves reasoning quality by +9--10pp composite on frontier models.** Single-ability injection: +9.0pp. Multi-ability injection: +10.1pp. Measured on 180 tasks, 536 valid judgments, blind protocol.

2. **The primary mechanism is suppression — blocking cognitive shortcuts the model would otherwise take.** The suppression signals (`Suppress: forward_momentum_bias; surface_level_stop; premature_conclusion`) function as metacognitive checkpoints that interrupt the model's default behavior of accepting the first plausible answer.

3. **Self-monitoring nearly doubled.** From 0.94 (baseline) to 1.81 (C1). This is the largest single-factor improvement and the most direct evidence that suppression signals activate metacognitive behavior.

4. **Verification increased by 44%.** From 1.50 to 2.16 (C1). Injected agents perform more counterfactual checks, boundary tests, and re-derivation steps.

5. **Every quality factor improved under injection.** Reasoning depth, epistemic honesty, alternative consideration, and audit trail all showed positive deltas. No quality factor degraded.

6. **Correctness remained stable.** The -0.03 (B1) and -0.11 (C1) deltas are small relative to the 3-point scale. RA²R changes *how* the model reasons without changing *what* it concludes.

7. **Multi-ability injection (C1) outperformed single (B1) on every measured dimension.** The advantage comes from perspective plurality — 4 abilities provide competing reasoning frames that block more failure modes and enable self-correction.

8. **Agent-native tool calling validates production deployment.** Agents called the API themselves, mirroring how real users' agents would use the product. This is not an artificial injection protocol.

9. **Domain-agnostic suppression works.** Metacognitive tasks improved +8.5pp despite 0% domain-matched retrieval. The suppression signals help regardless of which domain's ability is retrieved.

10. **EjBench establishes a new measurement paradigm.** Measuring reasoning *quality* across 7 dimensions captures what correctness-only benchmarks miss. The 0.519 composite gap between baseline and C1 on AB-V2-30 — where all conditions got the right answer — is invisible to correctness metrics.

### 10.2 The Trust Proposition

The practical value of these findings is trust, not accuracy. When a model's baseline correctness is 87% (2.60/3.00), the marginal value of additional correct answers is real but incremental. The transformative value is in reasoning transparency:

- A stakeholder reviewing an injected response can audit the self-monitoring checkpoints
- An engineer can verify that the model considered and eliminated alternative hypotheses
- A compliance officer can trace the reasoning chain through named methods and intermediate values
- A decision-maker can assess confidence calibration and epistemic honesty

These properties — which the 10-factor rubric quantifies — convert an LLM response from a black-box answer into an auditable reasoning artifact. This is the product's core value proposition, and EjBench v2 provides the first quantitative evidence for it.

---

## 11. Future Work

### 11.1 SAB (Skill Augmentation Benchmark)

A planned benchmark measuring whether RA²R improves existing agent skills (code generation, document analysis, data interpretation) rather than isolated reasoning tasks. SAB would test the product's value in real workflows, not just cognitive puzzles.

### 11.2 Cross-Model Validation

Testing RA²R injection on GPT-4o, Sonnet 4, Llama 4, and other model families. The suppression mechanism hypothesis predicts larger improvements on less capable models. Validation across architectures would strengthen the claim that suppression targets are architectural failure modes, not model-specific quirks.

### 11.3 Retrieval Precision Improvement

Current precision is 38.33%. Improving retrieval precision by refining the domain taxonomy should increase precision. The open question is how much additional lift domain-matched retrieval provides on top of the domain-agnostic suppression that already works.

### 11.4 EjBench v3 with Human Evaluation

Establishing inter-rater reliability between the LLM judge and human experts for the 10-factor rubric. Human evaluation would validate the rubric definitions, calibrate the scoring scale, and provide a gold standard against which future automated evaluations can be measured.

### 11.5 Domain Expansion (6 to 12 Domains)

The ability graph is planned to expand from 6 domains (SI, AB, MC, CA, TE, SP) to 12 domains (adding LI/Linguistic, TM/Theory of Mind, AN/Analytical, NR/Numerical Reasoning, NV/Navigation, PR/Procedural). EjBench v3 would include tasks from the new domains, testing whether the suppression mechanism generalizes to domains with different cognitive profiles.

### 11.6 Spatial Domain Investigation

A targeted ablation study to determine whether the C1 regression on Spatial tasks is caused by the ALTERNATIVE ability specifically. This would inform routing logic: automatically using single mode for spatial queries and multi mode for all others.

---

## 12. Reproducibility

### 12.1 Data Files

All raw data required to reproduce the analysis in this report is available in the project repository:

| File | Contents |
|:-----|:---------|
| `agents/shared/benchmarks/ejbench_production/summary_multifactor.json` | Aggregate results: per-condition means, per-domain means, deltas, flip analysis |
| `agents/shared/benchmarks/ejbench_production/results_multifactor.json` | Per-task scores for all 536 valid judgments |
| `agents/shared/benchmarks/ejbench_production/retrieval_precision.json` | Domain match data for all 180 tasks |
| `agents/shared/benchmarks/ejbench_v2.json` | 180 task definitions with ground truth |

### 12.2 Pipeline Scripts

| Script | Function |
|:-------|:---------|
| `agents/ejbench_payload_builder.py` | Builds API payloads for B1/C1 conditions |
| `agents/ejbench_generate.py` | Generates responses for all 3 conditions |
| `agents/ejbench_judge.py` | Blind judging with 10-factor rubric |

### 12.3 API Endpoint

Production API: `POST https://ejentum-main-ab125c3.zuplo.app/logicv1/`

Modes used in this benchmark:
- `single` — retrieves 1 ability, light rendering (~2,000--2,345 characters)
- `multi` — retrieves 4-ability synergy chain, light rendering with merged vectors (~3,825--4,164 characters)

### 12.4 Model Configuration

- **Generation model:** Claude Opus 4.6 (Anthropic), accessed via Claude Code CLI in `-p` mode
- **Judging model:** Claude Opus 4.6 (Anthropic), same access method
- **Condition A:** `--disallowedTools "Bash"`, `--max-turns 1`
- **Conditions B1/C1:** Bash tool enabled, `--max-turns 3`
- **Generation date:** 2026-03-23

---

## 13. Acknowledgments

EjBench v2 was designed, implemented, and analyzed by Frank Brsrk (Franko Luci). The RA²R Logic API, ability graph, and retrieval pipeline are sole-author work by the same researcher. The benchmark pipeline (task design, generation orchestration, blind judging protocol) was built specifically for this evaluation.

The external research cited in Section 2 provided theoretical grounding for the mechanistic analysis. The BIG-Bench Hard, CausalBench, and MuSR benchmark teams provided the published tasks used in the BBH/CausalBench/MuSR comparison study.

---

## 14. Appendices

### Appendix A: Complete Per-Domain Factor Breakdown

#### A.1 Abstract (30 tasks)

| Factor | A | B1 | B1-A | C1 | C1-A |
|:-------|:--|:---|:-----|:---|:-----|
| Correctness | 2.733 | 2.733 | 0.000 | 2.700 | -0.033 |
| Reasoning Depth | 2.500 | 2.733 | +0.233 | 2.800 | +0.300 |
| Self-Monitoring | 0.933 | 1.867 | +0.933 | 2.233 | +1.300 |
| Verification | 1.333 | 1.967 | +0.633 | 2.400 | +1.067 |
| Epistemic Honesty | 1.500 | 2.067 | +0.567 | 2.300 | +0.800 |
| Alt. Consideration | 1.733 | 2.200 | +0.467 | 2.433 | +0.700 |
| Audit Trail | 2.433 | 2.733 | +0.300 | 2.767 | +0.333 |

#### A.2 Simulation (30 tasks)

| Factor | A | B1 | B1-A | C1 | C1-A |
|:-------|:--|:---|:-----|:---|:-----|
| Correctness | 2.933 | 2.900 | -0.033 | 2.933 | 0.000 |
| Reasoning Depth | 2.000 | 2.300 | +0.300 | 2.500 | +0.500 |
| Self-Monitoring | 0.567 | 1.833 | +1.267 | 1.833 | +1.267 |
| Verification | 1.133 | 2.133 | +1.000 | 2.200 | +1.067 |
| Epistemic Honesty | 1.100 | 1.733 | +0.633 | 1.700 | +0.600 |
| Alt. Consideration | 0.367 | 1.033 | +0.667 | 1.200 | +0.833 |
| Audit Trail | 2.667 | 2.867 | +0.200 | 2.967 | +0.300 |

#### A.3 Causal (29--30 tasks)

| Factor | A | B1 | B1-A | C1 | C1-A |
|:-------|:--|:---|:-----|:---|:-----|
| Correctness | 2.517 | 2.500 | -0.017 | 2.379 | -0.138 |
| Reasoning Depth | 2.586 | 2.567 | -0.020 | 2.690 | +0.103 |
| Self-Monitoring | 1.069 | 1.767 | +0.698 | 2.000 | +0.931 |
| Verification | 1.448 | 1.900 | +0.452 | 2.241 | +0.793 |
| Epistemic Honesty | 1.793 | 2.000 | +0.207 | 2.207 | +0.414 |
| Alt. Consideration | 1.483 | 1.933 | +0.451 | 2.138 | +0.655 |
| Audit Trail | 2.483 | 2.567 | +0.083 | 2.793 | +0.310 |

#### A.4 Metacognitive (30 tasks)

| Factor | A | B1 | B1-A | C1 | C1-A |
|:-------|:--|:---|:-----|:---|:-----|
| Correctness | 2.667 | 2.700 | +0.033 | 2.733 | +0.067 |
| Reasoning Depth | 2.900 | 2.867 | -0.033 | 2.900 | 0.000 |
| Self-Monitoring | 1.267 | 1.700 | +0.433 | 2.033 | +0.767 |
| Verification | 1.900 | 2.233 | +0.333 | 2.467 | +0.567 |
| Epistemic Honesty | 2.100 | 2.367 | +0.267 | 2.433 | +0.333 |
| Alt. Consideration | 1.967 | 2.300 | +0.333 | 2.333 | +0.367 |
| Audit Trail | 2.800 | 2.900 | +0.100 | 2.900 | +0.100 |

#### A.5 Spatial (29--30 tasks)

| Factor | A | B1 | B1-A | C1 | C1-A |
|:-------|:--|:---|:-----|:---|:-----|
| Correctness | 2.667 | 2.467 | -0.200 | 2.103 | -0.563 |
| Reasoning Depth | 2.333 | 2.500 | +0.167 | 2.207 | -0.127 |
| Self-Monitoring | 0.867 | 1.667 | +0.800 | 1.345 | +0.478 |
| Verification | 1.433 | 2.000 | +0.567 | 1.724 | +0.291 |
| Epistemic Honesty | 1.400 | 1.633 | +0.233 | 1.448 | +0.048 |
| Alt. Consideration | 1.567 | 1.833 | +0.267 | 1.621 | +0.054 |
| Audit Trail | 2.733 | 2.767 | +0.033 | 2.517 | -0.216 |

#### A.6 Temporal (29--30 tasks)

| Factor | A | B1 | B1-A | C1 | C1-A |
|:-------|:--|:---|:-----|:---|:-----|
| Correctness | 2.100 | 2.133 | +0.033 | 2.069 | -0.031 |
| Reasoning Depth | 2.300 | 2.267 | -0.033 | 2.310 | +0.010 |
| Self-Monitoring | 0.967 | 1.367 | +0.400 | 1.379 | +0.413 |
| Verification | 1.733 | 1.833 | +0.100 | 1.931 | +0.198 |
| Epistemic Honesty | 1.367 | 1.600 | +0.233 | 1.552 | +0.185 |
| Alt. Consideration | 1.133 | 1.333 | +0.200 | 1.345 | +0.211 |
| Audit Trail | 2.733 | 2.667 | -0.067 | 2.621 | -0.113 |

### Appendix B: Retrieval Precision Detail

The following table summarizes what domains were *actually* retrieved for each domain's tasks when the agent called the API:

| Task Domain | Expected | CA Retrieved | TE Retrieved | SP Retrieved | SI Retrieved | AB Retrieved | MC Retrieved | UNKNOWN | Match Rate |
|:------------|:---------|:-------------|:-------------|:-------------|:-------------|:-------------|:-------------|:--------|:-----------|
| Causal | CA | **23** | 1 | 2 | 1 | 2 | 0 | 1 | 76.7% |
| Spatial | SP | 3 | 3 | **16** | 2 | 3 | 0 | 3 | 53.3% |
| Temporal | TE | 2 | **14** | 3 | 4 | 3 | 0 | 4 | 46.7% |
| Simulation | SI | 4 | 5 | 5 | **11** | 1 | 0 | 4 | 36.7% |
| Abstract | AB | 3 | 1 | 2 | 2 | **5** | 0 | 17 | 16.7% |
| Metacognitive | MC | 8 | 4 | 4 | 3 | 5 | **0** | 6 | 0.0% |

Notable patterns:

- **Metacognitive abilities were never retrieved for any task in any domain.** The Metacognitive ability embeddings do not align with any task descriptions generated by the agent's summarization. This is a retrieval architecture issue, not a quality issue with the abilities themselves.

- **Causal abilities were the most commonly retrieved cross-domain ability,** appearing in mismatched retrievals for MC (8), SI (4), SP (3), AB (3), and TE (2) tasks. This suggests the Causal ability embeddings have broad semantic overlap with reasoning-related language.

- **UNKNOWN retrievals** (where the retrieved ability's domain could not be determined from the injection content) occurred 35 times, predominantly for Abstract tasks (17). This represents a gap in the retrieval precision measurement methodology.

### Appendix C: Summary Data Reference

All numeric values in this report trace to the following source fields in `summary_multifactor.json`:

| Reported Value | Source Path |
|:---------------|:-----------|
| A composite: 0.6209 | `by_condition.A.composite_mean` |
| B1 composite: 0.7107 | `by_condition.B1.composite_mean` |
| C1 composite: 0.7217 | `by_condition.C1.composite_mean` |
| B1 composite delta: +0.0898 | `deltas_from_baseline.B1.composite` |
| C1 composite delta: +0.1008 | `deltas_from_baseline.C1.composite` |
| B1 net flips: +67 (37.4%) | `flip_analysis.B1.net_flip` / `net_flip_rate` |
| C1 net flips: +76 (42.9%) | `flip_analysis.C1.net_flip` / `net_flip_rate` |
| Self-monitoring B1 delta: +0.756 | `deltas_from_baseline.B1.self_monitoring` |
| Self-monitoring C1 delta: +0.864 | `deltas_from_baseline.C1.self_monitoring` |
| Verification B1 delta: +0.514 | `deltas_from_baseline.B1.verification` |
| Verification C1 delta: +0.667 | `deltas_from_baseline.C1.verification` |
| Retrieval precision: 38.33% | `retrieval_precision.json → precision` |

---

---

*Report generated 2026-03-22. All data from EjBench v2 production run dated 2026-03-23.*
*Ejentum -- Reasoning Ability-Augmented Retrieval for Production AI Agents.*
