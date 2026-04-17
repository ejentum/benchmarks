# Cognitive Scaffolding in Extended LLM Context Windows

**Author:** Frank Brsrk (Franko Luci), Ejentum
**Status:** Research thesis — observed 2026-03-18, pending formal validation
**Origin:** Live observation during 50+ tool-call file reorganization session with vector-retrieved abilities active in context

---

## 1. Thesis Statement

> **Reasoning Ability-Augmented Retrieval (RA²R) does not augment the model's reasoning ceiling. It prevents decay toward the model's reasoning floor across extended execution chains.** The cognitive abilities act as persistent attention anchors — structurally distinctive tokens that resist the natural dilution of reasoning-level constraints as task-specific tokens flood the context window.

The longer the task, the more the injection matters.

---

## 2. The Observation

During a 50+ tool-call session reorganizing the Ejentum codebase, 5 cognitive abilities were retrieved from the vector database and injected into context. The operator (reviewing the model's internal reasoning trace) observed:

1. The model internally referenced "I still have 5 abilities active in my context" — treating them as **live working state**, not historical artifacts.
2. The abilities were not re-read or explicitly invoked during execution. They influenced attention allocation passively — the model's reasoning steps aligned with the injected cognitive operations without conscious application.
3. The model self-assessed the abilities as providing "minimal difference" on its reasoning — but this assessment itself may be a ceiling effect. The model cannot A/B test itself within a single session.

**Key inference:** The abilities didn't teach the model anything new. They occupied attention weight that prevented reasoning patterns from decaying as the context filled with low-reasoning tokens (bash outputs, file listings, move confirmations).

---

## 3. Theoretical Framework

### 3.1 Attention Decay in Multi-Step Execution

Transformer self-attention computes pairwise relevance across all context tokens. This is not uniform:

- **Lost-in-the-middle effect** (Liu et al., 2023): LLMs attend reliably to beginning and end of context; middle-positioned information receives degraded attention.
- **Recency bias**: Recent tokens dominate attention allocation during generation. As tool outputs accumulate, they push earlier reasoning instructions into the attention dead zone.
- **Token-type competition**: A `mv` command and a reasoning DAG both occupy tokens, but the `mv` command is immediately actionable while the DAG is structurally relevant. Without structural distinctiveness, the DAG loses the attention competition.

**Implication:** In a 50-step execution, initial reasoning instructions (plan, constraints, cognitive operations) migrate from high-attention positions to mid-context positions where attention is weakest. The model hasn't forgotten them — but it's no longer actively reasoning with them.

### 3.2 The Working Memory Bottleneck

A transformer's effective "working set" during any single generation step isn't the full context window. Attention head specialization research shows most heads attend to a narrow token subset per step. The effective working set is hundreds of tokens, not millions.

**MC-008 (Cognitive Load Detector)** formalizes this as the 7-element ceiling — Miller's number applied to concurrent reasoning elements. The model can track ~7 unchunked reasoning elements per generation step. In a reorganization task, those 7 slots fill with: current file path, target directory, script being patched, import being fixed, remaining files, verification state, next phase.

The cognitive operations (MECE checking, consistency verification, reversibility assessment) compete for those same 7 slots. Without persistent anchors, they lose.

### 3.3 Why DAG Notation Acts as an Attention Anchor

The DAG format (`S1:action → G1{test?} --yes→ S2 --no→ HALT`) has properties that create disproportionate attention weight:

| Property | Mechanism | Effect |
|----------|-----------|--------|
| **Symbolic structure** | Arrows, braces, pipes create high-entropy token sequences | Stand out from natural language and bash output |
| **Procedural encoding** | It's a program, not a description | Transformer treats it as actionable, not informational |
| **Gate predicates** | `G1{count>7?}` is a testable condition | Provides concrete check, not vague guideline |
| **N-nodes** | `N{carry_unchunked_elements}` is explicit prohibition | Prohibition is structural, not derived |
| **Register distinctiveness** | Unlike any other token type in context | Attention mechanism allocates weight to novel patterns |

A compact structured DAG commands attention weight normally reserved for thousands of natural language tokens because it occupies a unique *register* that doesn't pattern-match to routine context.

### 3.4 The M-Node as Meta-Cognitive Heartbeat

M-nodes are scheduled self-audits embedded in the topology:

> *"Every 2 cycles after count passes threshold, verify: is element count accurate or are compound variables counted as singles?"*

This isn't a reasoning step. It's a **defragmentation routine** — it forces the model to periodically re-attend to its own reasoning structure rather than staying in execution mode. Without M-nodes, a model can execute 20+ tool calls without ever checking whether it's still aligned with the original reasoning frame.

In the context window liveliness framing: M-nodes are **attention re-focusing interrupts** that prevent sustained execution-mode tunnel vision.

### 3.5 SP-006 (Relational Invariant Maintainer) as Post-Transform Validator

`PRE:S0:freeze(R1..RN_definitions) → S1:enumerate_all_relationships → for_each_relationship → G1{holds?} --no→ adjust`

This ability's `PRE:freeze` instruction anchors the starting state, then its loop structure ensures every transformation is checked against all relational contracts. In a file reorganization with 60+ moves and 21 script patches, this pattern prevents the failure mode where individual moves are correct but cross-references break.

The ability doesn't need to be explicitly invoked. Its presence in context maintains the *expectation* that relational invariants should be checked — biasing the model toward verification behavior.

### 3.6 Multi-Ability Interaction: Compound Scaffolding in the Latent Space

The injection thesis describes persistence of a single ability. But in production (multi-injection, synergy chains), multiple abilities coexist in context simultaneously. They don't operate as independent anchors — they **interact within the model's latent attention space**.

**The mechanism:** Each ability occupies its own attention anchor position in context. When the transformer computes self-attention for a new generation step, it attends to ALL context tokens — including all co-present abilities. The attention computation produces cross-token interactions: the attention weights between Ability A's DAG and Ability B's DAG create implicit relational patterns that neither ability produces alone.

**What this means concretely:**

1. **Suppression vectors compound.** If Ability A suppresses `correlation_as_causation` and Ability B suppresses `anchoring_on_first_estimate`, the model encounters both prohibitions simultaneously during every generation step. The compound suppression surface is wider than either individual ability provides.

2. **Procedures cross-reference.** When Ability A's gate fires (`G1{root cause identified?}`), the checkpoint it creates in the output becomes an input that Ability B's procedure (`S1: project timeline from identified cause`) can build on. The abilities form a **reasoning pipeline** through attention interaction, not through explicit orchestration.

3. **M-nodes from different abilities create distributed self-auditing.** If three abilities each have an M-node checking a different aspect of reasoning quality (causal validity, temporal consistency, metacognitive drift), the model encounters all three self-audit prompts throughout execution. This creates a multi-dimensional monitoring injection that no single ability provides.

4. **Structural distinctiveness multiplies.** Multiple DAGs in context create a higher density of structurally distinctive tokens. The attention mechanism has more anchor points to reference, making the overall injection more resistant to dilution by execution tokens.

**The emergent property:** Multiple abilities in context produce a **cognitive injection** — not a list of independent instructions, but an interacting attention structure that maintains analytical discipline across extended execution chains. The injection has properties that none of its component abilities have individually: compound suppression, cross-referencing procedures, distributed self-auditing, and multiplicative attention anchoring.

**Testable prediction:** Multi-ability injection should show super-linear value at long chain lengths. At short chains (1-3 steps), adding a second ability may add marginal value. At long chains (25+ steps), the second ability's contribution should exceed its individual value because it reinforces the first ability's attention anchor and provides cross-referencing procedures that prevent compound drift.

This prediction is testable via a modification of B-SP1: run chain-length ablation with 1-ability vs. 3-ability conditions and measure whether the multi-ability advantage grows with chain length.

---

## 4. The Compound Drift Hypothesis

### Stated Precisely

> In multi-step LLM execution, each step introduces task-specific tokens that dilute attention to reasoning-level constraints. Without structural anchors, the probability of maintaining a specific cognitive operation decreases monotonically with step count. Cognitive ability injection creates persistent attention anchors that resist this decay, producing a injection effect whose value compounds over chain length.

### Formal Model

Let:
- `R(n)` = reasoning fidelity at step n (probability the model applies the correct cognitive operation)
- `d` = per-step decay rate (attention dilution from new tokens)
- `k` = number of active cognitive anchors in context
- `s(k)` = injection resistance factor (attention weight preserved by k anchors)

**Without injection:**
`R(n) = R(0) * (1 - d)^n`

Reasoning fidelity decays exponentially with step count.

**With injection:**
`R(n) = R(0) * (1 - d + s(k))^n`

If `s(k) >= d`, reasoning fidelity is maintained. If `s(k) < d`, decay is slowed but not eliminated.

### Predictions

| Task Length | Expected Delta (augmented - unaugmented) |
|-------------|---------------------------------------------|
| 1-3 steps | Near-zero (ceiling effect — both near R(0)) |
| 5-10 steps | Small but measurable (+2-5%) |
| 10-25 steps | Moderate (+5-15%) |
| 25-50 steps | Large (+10-25%) — compound drift accumulation |
| 50+ steps | Maximum divergence — unaugmented approaches floor |

### Existing Evidence (Partial)

| Data Point | Interpretation |
|------------|----------------|
| Beyond-Reasoning single-turn tasks: ceiling on 4/7 signals | Short chains — injection adds little |
| Phase 4 HARD tasks: small deltas between conditions | Moderate chains — modest injection effect |
| Phase 4 EXTREME tasks: C2 dominates at 0.785 vs 0.769 baseline | Longer chains — injection matters more |
| v6 blind eval (multi-factor professional problems): +7.0 lift | Sustained reasoning required — clear injection effect |
| RESEARCH_REPORT (5 domains, hard problems): +7.8 lift | Same pattern — problems requiring extended reasoning chains |

---

## 4b. Converging Evidence: Structure, Delivery, and Scaffolding as a Unified Mechanism

Three independent observations, discovered through adversarial self-examination (2026-03-19), converge into a single mechanism:

### Observation 1: Structure Is Procedure Compliance, Not Formatting

The +22.5% structure improvement from Beyond-Reasoning was initially interpreted as potential formatting bleed — the model echoing `prompt_override`'s numbered steps. Re-examination rejects this framing.

The `prompt_override` doesn't suggest a format. It prescribes a **cognitive procedure**: "Step 1: Decompose the causal chain. Step 2: Test for confounders. Step 3: Verify directionality." When the model follows these steps, it's executing a reasoning protocol, not copying a template. The +22.5% measures how often the model ran the full procedure instead of free-associating.

The low precision delta (+2.8%) on those same tasks is not evidence against the procedure — it's evidence that the tasks were too easy. The model was already getting roughly correct answers without the procedure. On hard tasks (v6 evaluation), the same procedure compliance produced +1.0 correctness and +1.4 reasoning depth — the procedure changed the final answer because the task was hard enough that skipping steps meant getting it wrong.

**Connection to injection:** Procedure compliance is what the injection maintains. The attention anchors don't preserve "information" — they preserve "what cognitive operation to execute next." Over extended chains, the model drifts from procedure into free-association. The abilities prevent that drift.

### Observation 2: Tool-Based Delivery Is the Product, Not a Feature

The same DAG content delivered via CLI injection produced negative results (v1-v4). Delivered via vector database tool retrieval, it produced +7.0 lift (v6). The content didn't change — the attention dynamics did.

Tool results occupy a privileged position in transformer attention: they are recent (recency bias), requested (the model has agency), and actionable (the model expects to use them). System prompt content decays into the attention dead zone as context grows. Tool results arrive at peak relevance.

**Connection to injection:** The tool-based delivery mechanism maximizes the initial attention weight of the ability. This creates a stronger anchor point that resists subsequent decay. The injection effect isn't just about the DAG notation's structural distinctiveness — it's also about *when and how* the ability enters context.

### Observation 3: The Compound Thesis

These observations are not independent findings. They are three facets of one mechanism:

1. **The abilities prescribe cognitive procedures** (not information, not formatting)
2. **Tool-based delivery ensures maximum initial attention weight** (agency + recency)
3. **DAG notation maintains attention weight across subsequent steps** (structural distinctiveness)
4. **The maintained attention preserves procedure compliance** (injection prevents drift to free-association)
5. **Procedure compliance produces better answers only when tasks are hard enough** (easy tasks don't need the procedure)
6. **Task difficulty correlates with chain length** (harder problems require more reasoning steps)
7. **Therefore: value compounds with chain length** (more steps = more drift = more injection value)

This produces a falsifiable product definition:

> **RA²R is a reasoning retrieval tool. Agents call it to receive cognitive operations delivered as tool results with maximum attention weight. The operations prescribe procedures that the model complies with. DAG notation maintains procedure compliance across extended execution by acting as a persistent attention anchor. The value is proportional to task difficulty and chain length — minimal on easy single-turn tasks, substantial on hard multi-step reasoning chains.**

Every piece of existing evidence is consistent with this definition. The decisive test is B-SP1 (chain-length ablation): if injection value does not increase with chain length, the compound thesis is wrong.

---

## 5. Product Positioning Reframe

### Old Frame (Incorrect)
> *"Ejentum makes LLMs smarter."*

Disproved by ceiling effects. The model is already capable.

### New Frame (Supported by Evidence)
> **"Ejentum prevents LLMs from getting dumber over extended execution."**

More precisely:
> **Ejentum maintains reasoning fidelity across context window lifespan.** The cognitive abilities act as persistent attention anchors that resist the natural decay of reasoning quality in multi-step LLM execution. The longer the task, the greater the value.

### Competitive Moat Implications

1. **Scales with task complexity** — as agentic AI tackles harder problems requiring more steps, the injection value increases
2. **Model-independent mechanism** — attention decay is architectural (all transformers), not model-specific
3. **Complementary to model improvements** — larger context windows create *more* attention decay surface, not less. Ejentum's value grows with context length.
4. **Not replicable by system prompts** — natural language instructions decay at the same rate as other tokens. DAG notation resists decay through structural distinctiveness.

---

## 6. Proposed Benchmark: Scaffolding Persistence Validation

### B-SP1: Chain-Length Ablation

**What it tests:** Delta between augmented and unaugmented performance as a function of reasoning chain length.

**Design:**
- 40 tasks, each decomposable into controlled step counts
- 4 step-count variants per task: 5, 10, 25, 50 steps (forced decomposition)
- 2 conditions per variant: A (baseline), B (vector-augmented with 3 abilities)
- Judge evaluates final output quality on 8-criterion rubric (same as v6)

**Tasks:** Design problems requiring sustained reasoning — policy analysis, multi-factor risk assessment, architectural review, diagnostic chains. Each task must have a verifiable correct conclusion that requires integrating information across all steps.

**Metric:** `injection_delta(n) = score_B(n) - score_A(n)` measured at each step count.

**Prediction:** `injection_delta` increases with `n`. Specifically:
- `injection_delta(5)` < 2 points
- `injection_delta(10)` ~ 3-5 points
- `injection_delta(25)` ~ 5-10 points
- `injection_delta(50)` > 10 points

**Falsification:** If `injection_delta` is flat across all step counts, the compound drift hypothesis is wrong and the value is one-shot priming, not sustained injection.

**Cost:** 40 tasks × 4 lengths × 2 conditions = 320 generations + 320 judgments = **640 LLM calls**

---

### B-SP2: Mid-Task Scaffolding Removal

**What it tests:** Whether abilities provide sustained value or one-shot priming by removing them from context mid-execution.

**Design:**
- 20 tasks, all requiring 25+ reasoning steps
- 3 conditions:
  - A: No injection (baseline)
  - B: Injection at start, maintained throughout
  - C: Injection at start, **removed at step 12** (context truncation simulated by explicitly instructing the model that the injected abilities are no longer applicable)
- Judge evaluates steps 1-12 and steps 13-25 separately

**Metric:** `decay_after_removal = score_C(steps 13-25) - score_B(steps 13-25)`

**Prediction:** If injection is sustained (not one-shot):
- `score_B(steps 13-25)` >> `score_C(steps 13-25)` — performance degrades after removal
- `score_C(steps 1-12)` ≈ `score_B(steps 1-12)` — equivalent while injection present

**Falsification:** If `score_C(steps 13-25)` ≈ `score_B(steps 13-25)`, the abilities are one-shot primers and the sustained injection hypothesis is wrong.

**Cost:** 20 tasks × 3 conditions = 60 generations + 120 judgments (split evaluation) = **180 LLM calls**

---

### B-SP3: Format Ablation (DAG vs. Prose)

**What it tests:** Whether structural distinctiveness of DAG notation contributes to the injection effect, or if equivalent semantic content in prose achieves the same result.

**Design:**
- 30 tasks requiring 15+ reasoning steps
- 3 conditions:
  - A: No injection (baseline)
  - B: Standard ability injection (DAG notation + structured fields)
  - C: Prose-equivalent injection (same cognitive content rewritten as natural language paragraphs, same token count ± 10%)
- Prose versions must preserve: the procedural steps, the gate conditions, the prohibitions, the M-node self-audit — but expressed as paragraphs, not symbolic notation.

**Metric:** `format_delta = score_B - score_C`

**Prediction:** If structural distinctiveness matters:
- `score_B > score_C` on tasks requiring 15+ steps (DAG resists attention decay better than prose)
- `score_B ≈ score_C` on short tasks (both formats within attention range)

**Falsification:** If `score_B ≈ score_C` across all step counts, the injection effect is semantic, not structural — meaning natural language instructions would work equally well.

**Cost:** 30 tasks × 3 conditions = 90 generations + 90 judgments = **180 LLM calls**

---

### B-SP4: Attention Probe (Open-Source Model)

**What it tests:** Direct measurement of attention weight allocated to ability tokens vs. position in context.

**Design:**
- Requires open-weight model (Llama-3-70B or Mistral Large)
- 10 tasks executed with ability injection
- At each generation step, extract attention weights from all heads for:
  - Ability tokens (DAG notation)
  - Plan tokens (initial instructions)
  - Recent tool output tokens
  - Mid-context informational tokens

**Metrics:**
- `ability_attention_persistence = mean(attention_to_ability_tokens)` across all generation steps
- `plan_attention_decay = attention_to_plan_at_step_N / attention_to_plan_at_step_1`
- `relative_salience = ability_attention / plan_attention` at each step

**Prediction:** If structural distinctiveness creates attention anchors:
- `ability_attention_persistence` remains above baseline across all steps
- `plan_attention_decay` shows exponential decay
- `relative_salience` increases with step count (abilities hold attention while plan decays)

**Falsification:** If ability tokens and plan tokens show identical decay curves, structural distinctiveness has no attention-anchoring effect.

**Cost:** 10 tasks × 1 condition, but requires attention extraction infrastructure. **~10 LLM calls + engineering effort.**

---

## 7. Consolidated Benchmark Roadmap

### Existing Pending Benchmarks (from Master Plan + Wave 2)

| ID | Benchmark | Status | Tasks | LLM Calls | Priority |
|----|-----------|--------|-------|-----------|----------|
| MP-1B | Multi-Logic v2 Rerun | BLOCKED | 60 | ~180 | Low |
| MP-2B | Light vs Legacy Ablation | PENDING | 140 | ~840 | Medium |
| MP-3 | 5-Condition Expansion | PENDING | 140 | ~1,400 | Medium |
| **MP-4** | **Structure/Correctness Decomposition** | **PENDING** | **140** | **~560** | **CRITICAL** |
| MP-5 | Adversarial Task Redesign (4 ceiling signals) | PENDING | 80 | ~800 | Medium |
| **MP-6** | **Cross-Model Benchmarks** | **PENDING** | **140** | **~4,200** | **CRITICAL** |
| MP-7 | Retrieval Precision (v2 Gemini re-baseline) | OPEN | 30 | ~30 | High |
| MP-8 | Multi-Agent Pipeline | PENDING | 20 | ~120 | High |
| **MP-9** | **Production E2E Validation** | **OUTSTANDING** | **12** | **~12** | **CRITICAL** |
| MP-10 | Documentation/Publication | PENDING | — | 0 | High |
| MP-11 | Longitudinal Tracking Setup | PENDING | — | 0 | Low |
| W2-L1 | Retrieval Precision Gate | PLANNING | 120 | 0 | BLOCKER |
| **W2-L2** | **Injection-Dependent Correctness** | **PLANNING** | **120** | **~1,520** | **CRITICAL** |
| W2-L3 | Structure/Correctness Decomp (dual-judge) | PLANNING | 60 | ~480 | High |
| W2-L4 | Negative Gate Ablation | PLANNING | 60 | 0 | Medium |
| W2-L5 | Cross-Model Generalization (Wave 2) | PLANNING | 40 | ~240 | High |
| W2-L6 | Compositional Value | PLANNING | 40 | ~320 | Medium |
| W2-L7 | Multi-Agent Pipeline (Wave 2) | PLANNING | 20 | ~180 | Medium |
| W2-L8 | Adversarial Domain-Cross | PLANNING | 20 | 0 | Low |
| W2-L9 | Procedure Compliance Verification | PLANNING | 60 | 0 | High |

### New Scaffolding Persistence Benchmarks

| ID | Benchmark | Status | Tasks | LLM Calls | Priority |
|----|-----------|--------|-------|-----------|----------|
| **B-SP1** | **Chain-Length Ablation** | **PROPOSED** | **40** | **~640** | **HIGH** |
| **B-SP2** | **Mid-Task Scaffolding Removal** | **PROPOSED** | **20** | **~180** | **HIGH** |
| **B-SP3** | **Format Ablation (DAG vs Prose)** | **PROPOSED** | **30** | **~180** | **MEDIUM** |
| **B-SP4** | **Attention Probe (open model)** | **PROPOSED** | **10** | **~10 + infra** | **HIGH (publishable)** |

### Recommended Execution Order

**Phase 1: Foundation (blocks everything)**
1. MP-7 — Retrieval precision re-baseline (~30 calls)
2. MP-9 — Production E2E validation (~12 calls)
3. PHASE3_FIX_PLAN Tasks 1-7 — Engineering prerequisites

**Phase 2: Core Evidence (blocks marketing claims)**
4. W2-L1 — Retrieval precision gate (0 calls, blocking checkpoint)
5. W2-L2 — Injection-dependent correctness (~1,520 calls)
6. MP-4 — Structure/correctness decomposition (~560 calls)
7. W2-L9 — Procedure compliance verification (0 calls)

**Phase 3: Scaffolding Validation (new thesis)**
8. **B-SP1** — Chain-length ablation (~640 calls) — **the decisive test**
9. **B-SP3** — Format ablation (~180 calls) — tests structural distinctiveness
10. **B-SP2** — Mid-task removal (~180 calls) — tests sustained vs. one-shot

**Phase 4: Generalization (blocks model-agnostic claim)**
11. MP-6 / W2-L5 — Cross-model benchmarks (~4,200 calls)
12. **B-SP4** — Attention probe on open model (~10 calls + infra)

**Phase 5: Depth & Completion**
13. MP-8 / W2-L7 — Multi-agent pipeline (~180 calls)
14. W2-L6 — Compositional value (~320 calls)
15. MP-5 — Adversarial task redesign (~800 calls)
16. MP-10 — Documentation/publication
17. MP-11 — Longitudinal tracking

### Total New Cost

B-SP1 through B-SP4: **~1,010 LLM calls** (~$18 at Claude API rates)

---

## 8. Retrieved Cognitive Abilities (Active During Thesis Development)

### MC-008 — Cognitive Load Detector
**Contribution:** Formalized the 7-element working memory ceiling and its application to transformer effective working sets. The M-node pattern ("verify compound variables aren't falsely chunked") directly informed Section 3.4 on meta-cognitive heartbeats.

**DAG:** `S1:list_and_count → G1{>7?} → chunk → M1{verify chunks genuinely cohere} → validate_boundary_conditions → OUT`

### SP-006 — Relational Invariant Maintainer
**Contribution:** Provided the `PRE:freeze → for_each_relationship → verify_holds` pattern that maps to the injection mechanism: freeze reasoning constraints at injection time, then verify they're maintained across transformations.

**DAG:** `PRE:S0:freeze(R1..RN) → enumerate_relationships → for_each → check_invariant → G1{holds?} → adjust_or_confirm → OUT`

### AB-010 — Ontological Constructor (from reorganization session)
**Contribution:** MECE enforcement pattern that maintained category coherence across 60+ file moves.

### SP-028 — Cross-Pillar Consistency Guardian (from reorganization session)
**Contribution:** Pairwise consistency checking pattern that drove the final path-reference sweep.

### AB-033 — Path Diversity Explorer (from reorganization session)
**Contribution:** Minimal direct use — but its presence in context may have contributed to the model considering script patch alternatives rather than committing to the first viable approach.

---

## 9. Open Questions

1. **Is the injection effect linear or threshold-based?** Does it turn on at a specific chain length, or is it proportional throughout?
2. **Does ability count matter?** Is 1 ability sufficient, or does injection effectiveness increase with the number of active abilities (diminishing returns expected)?
3. **What's the minimum structural distinctiveness needed?** Would simplified DAG notation (just arrows and labels, no M-nodes) still anchor attention?
4. **Does the effect transfer across conversation turns?** In multi-turn sessions, do abilities injected in turn 1 still injection reasoning in turn 5?
5. **Can injection be adversarial?** If a wrong-domain ability is injected, does it anchor the *wrong* cognitive operation with the same persistence? (This would be both a risk and further evidence of the mechanism.)

---

*Document created: 2026-03-18*
*Origin: Live observation during Ejentum v3.8 file reorganization*
*Authors: Frank + Claude Opus 4.6 (collaborative analysis)*
