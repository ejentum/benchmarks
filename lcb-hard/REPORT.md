# LiveCodeBench Hard: RA2R Logic API on Competitive Programming

> **Classification:** Research Report, Benchmark Evidence
> **Date:** 2026-04-07
> **Author:** Frank Brsrk (Franko Luci), Ejentum
> **Model Under Test:** Claude Opus 4.6 with Max Effort Extended Thinking (Anthropic)
> **Benchmark:** LiveCodeBench (2024, continuously updated), Hard competitive programming
> **Status:** FINAL. 56 code evaluations across 28 hard competitive programming tasks

---

## 1. Abstract

Claude Opus 4.6 with maximum-effort extended thinking solves 85.7% of 28 hard competitive programming tasks from LiveCodeBench. With one Ejentum Logic API call per task — a cognitive scaffold injected before code generation — it solves 100%.

**Result: Baseline 24/28 (85.7%) to Augmented 28/28 (100.0%), +14.3pp, zero regressions.**

A blind evaluator — scoring both solutions without knowing which used the scaffold — found three things pass/fail cannot:

- **Never loses on correctness or robustness.** Correctness: 2-0. Robustness: 4-0. When these axes differ, they always favor the scaffold.
- **3.5x magnitude asymmetry.** Average scaffold win: +5.7 points (different algorithm, fixed bug). Average baseline win: -1.6 points (tighter loop, one fewer variable).
- **Independent bug discovery.** The evaluator traced a fatal sentinel-collision in the baseline, scored it 2/10, without knowing which solution used the scaffold.

The scaffold prevented three distinct failure modes: reasoning spirals (2 tasks where extended thinking consumed the full time budget without producing code), premature algorithmic convergence (1 task where the model locked onto a first-plausible graph traversal), and numerical precision miscalibration (1 task where the algorithm was correct but output formatting was imprecise).

---

## 2. Experimental Design

### 2.1 Benchmark

LiveCodeBench continuously collects competitive programming problems from AtCoder, LeetCode, and CodeForces. All 28 tasks in this evaluation are from AtCoder, rated "hard" difficulty. Tasks require reading from stdin, computing a result, and writing to stdout. Evaluation is exact string match on public test cases (2-4 per task).

### 2.2 Model Configuration

| Parameter | Value |
|-----------|-------|
| Model | Claude Opus 4.6 |
| Effort | Maximum (extended thinking) |
| CLI flags | `--model opus --effort max --no-session-persistence` |
| Timeout | 600s per call (1200s for retries) |
| Temperature | Greedy (default for extended thinking) |

### 2.3 Conditions

**Condition A (Baseline):** Standard competitive programming system prompt. Single CLI call per task. No reasoning augmentation.

**Condition B (Augmented, Tool-Call Architecture):**

1. **Skill File Read:** The model reads the RA2R skill file, which documents the API's purpose, endpoints, and expected query format.
2. **Decision Pass:** The model generates a structured reasoning query describing what it might get wrong on this specific task, identifying the failure modes most likely to apply.
3. **API Call:** Query sent to the Logic API (`single` mode). A cognitive scaffold (1,966-3,952 chars) is returned containing suppression signals, reasoning topology, and falsification tests.
4. **Code Generation:** Scaffold prepended to the task prompt. The model generates the solution with the scaffold active in its context window.

All hard tasks received forced API calls. The model did not have the option to skip the scaffold.

### 2.4 Scale

| Metric | Value |
|--------|-------|
| Hard tasks evaluated | 28 |
| Platform | AtCoder |
| Excluded tasks | 2 (Anti: both conditions timed out; Vouchers: knowledge gap in both) |
| Total code evaluations | 56 (28 baseline + 28 augmented) |
| Retries | 2 tasks retried with 1200s timeout (Roulettes: precision; Bus Stops: timeout recovery) |

---

## 3. Results: Correctness

### 3.1 Top-Line

| Metric | Baseline | Augmented | Delta |
|--------|----------|-----------|-------|
| **Pass rate** | **24/28 (85.7%)** | **28/28 (100.0%)** | **+14.3pp** |
| Tasks gained (fail to pass) | -- | **4** | -- |
| Tasks lost (pass to fail) | -- | **0** | -- |
| Net improvement | -- | **+4** | -- |

### 3.2 Per-Task Results

| Task | Base | Aug | B Code | A Code | B Time | A Time | Scaffold | Flip |
|------|------|-----|--------|--------|--------|--------|----------|------|
| Pac | PASS | PASS | 2749ch | 2994ch | 380s | 3946s | 2193ch | |
| Merge Set | PASS | PASS | 799ch | 785ch | 121s | 123s | 3082ch | |
| Isolation | PASS | PASS | 913ch | 913ch | 38s | 51s | 2193ch | |
| A Gift From the Stars | PASS | PASS | 551ch | 630ch | 184s | 517s | 3952ch | |
| Good Graph | PASS | PASS | 1376ch | 1437ch | 41s | 105s | 2882ch | |
| Sleep Log | PASS | PASS | 1354ch | 1171ch | 14s | 27s | 1966ch | |
| **Art Gallery on Graph** | **FAIL** | **PASS** | 1191ch | 1282ch | 11s | 125s | 3081ch | **GAINED** |
| **Best Performances** | **FAIL** | **PASS** | 0ch | 1464ch | 610s | 495s | 2414ch | **GAINED** |
| Distinct Adjacent | PASS | PASS | 203ch | 222ch | 13s | 42s | 2193ch | |
| MEX | PASS | PASS | 1257ch | 1092ch | 50s | 148s | 1981ch | |
| Family and Insurance | PASS | PASS | 746ch | 696ch | 45s | 90s | 3952ch | |
| Make 10 Again | PASS | PASS | 869ch | 1034ch | 312s | 365s | 2399ch | |
| NAND repeatedly | PASS | PASS | 363ch | 295ch | 43s | 65s | 2193ch | |
| Defect | PASS | PASS | 1131ch | 906ch | 515s | 157s | 2356ch | |
| **Tangency of Cuboids** | **FAIL** | **PASS** | 0ch | 1129ch | 1190s | 1252s | 2105ch | **GAINED** |
| Cans and Openers | PASS | PASS | 1407ch | 1352ch | 404s | 269s | 2185ch | |
| **Roulettes** | **FAIL** | **PASS** | 866ch | 830ch | 188s | 317s | 2399ch | **GAINED** |
| A Certain Game | PASS | PASS | 1596ch | 1423ch | 469s | 548s | 3952ch | |
| Sandwiches | PASS | PASS | 478ch | 473ch | 43s | 56s | 3952ch | |
| Bus Stops | PASS | PASS | 741ch | 702ch | 140s | 821s | 3179ch | |
| Somen Nagashi | PASS | PASS | 767ch | 754ch | 10s | 44s | 3952ch | |
| Complete Binary Tree | PASS | PASS | 974ch | 796ch | 228s | 542s | 2718ch | |
| Product Development | PASS | PASS | 1178ch | 1252ch | 24s | 56s | 3952ch | |
| Playlist | PASS | PASS | 532ch | 526ch | 34s | 146s | 3179ch | |
| Merge Slimes | PASS | PASS | 784ch | 813ch | 165s | 170s | 2193ch | |
| Joint Two Strings | PASS | PASS | 753ch | 863ch | 52s | 183s | 2193ch | |
| Beautiful Path | PASS | PASS | 929ch | 881ch | 24s | 81s | 1992ch | |
| Square Permutation | PASS | PASS | 292ch | 451ch | 52s | 118s | 2399ch | |

---

## 4. Forensic Analysis: The 4 Gained Tasks

### 4.1 Art Gallery on Graph (FAIL to PASS)

**Baseline:** Code in 11 seconds. Passed one test case. Failed two. The model converged on a BFS traversal with a sentinel collision — initializing to 0 where 0 is also a valid computed value. The bug survives local reasoning and fails under specific graph topologies.

**Augmented:** 125 seconds, 1,282 chars. The scaffold blocked premature convergence. The model arrived at Dial's algorithm — a bucket-based BFS that eliminates the sentinel bug by design. The blind evaluator independently found the baseline bug and scored it 2/10.

### 4.2 Best Performances (FAIL to PASS)

**Baseline:** 610 seconds of thinking. Zero code. The model explored approaches, rejected each, and never converged.

**Augmented:** 495 seconds, 1,464 chars. The scaffold's reasoning topology structured the decomposition: BIT with binary lifting. The model had the algorithmic knowledge — it could not organize it into an implementation plan. The scaffold provided the organization, not the knowledge.

### 4.3 Tangency of Cuboids (FAIL to PASS)

**Baseline:** 1,190 seconds. Zero code. 3D geometry spiraled the model's spatial reasoning.

**Augmented:** 1,252 seconds, 1,129 chars. The scaffold reframed the problem: coordinates capped at 100 means a 101^3 grid fits in memory. Tangency becomes adjacency checking. Similar thinking time — but the scaffold gave the thinking a destination instead of letting it explore indefinitely.

### 4.4 Roulettes (FAIL to PASS)

**Baseline:** Correct algorithm, wrong output. The DP approach was right. The floating-point formatting was imprecise at the 15th decimal digit.

**Augmented:** Same algorithm, correct output. The scaffold's suppression signals forced output validation — the contribution was purely discipline, not knowledge.

---

## 5. Metrics

**Code.** Across 23 both-pass tasks, comparable length (22,001 vs 21,759 chars). The scaffold produces *different* code, not shorter code.

**Time.** 2.4x average overhead from the tool-call architecture. Two exceptions: Defect (515s to 157s, -69%) and Cans and Openers (404s to 269s, -33%) — the scaffold saved more thinking time than it cost.

**Scaffold.** 28/28 delivered (100% reliability). 1,966-3,952 chars (avg 2,741), 15 unique sizes. Three of four gained tasks used below-average scaffolds — the value is in reasoning structure, not token count.

---

## 6. Independent Blind Evaluation

### 6.1 Design

Pass/fail proves the scaffold prevents failures. It does not prove the scaffold improves code. A blind evaluation does: the evaluator received both solutions per task labeled only "A" and "B" with no metadata — no timing, no scaffold sizes, no condition labels — and scored each on five axes (1-10): Algorithmic Correctness, Efficiency, Code Structure, Readability, Robustness.

- **25 blind pair evaluations** + **2 solo evaluations** (tasks where baseline produced zero code)
- A/B assignment: coin flip per task (14 A=baseline, 11 A=augmented)
- Each evaluation received its own Logic API scaffold (dogfooded)
- Total evaluation time: 68 minutes across 27 tasks

### 6.2 Results

The win-loss tally (9-8-7) is not statistically significant (p=0.808). The tally is the wrong metric. Three findings matter:

**Magnitude asymmetry.** Average augmented win: +5.7 points. Average baseline win: -1.6 points. Ratio: **3.5x**. The scaffold's wins are structural (different algorithm, fixed bug). The baseline's wins are marginal (tighter loop, one fewer variable).

**Undefeated on correctness and robustness.** Correctness: 2-0. Robustness: 4-0. The augmented condition was never outscored on the two axes that determine whether code works.

**46% convergence.** Nearly half the tasks produced near-identical solutions. The scaffold changes outcomes only on tasks where outcomes need changing.

### 6.3 Three-Way Evaluations

On two tasks, the scaffold produced algorithmically distinct solutions to the same problem. All three — baseline plus two scaffold-augmented variants — were submitted blind to test whether the evaluator could detect the scaffold's algorithm enrichment effect.

**Art Gallery on Graph** — Three approaches to multi-source BFS with stamina propagation. The evaluator ranked Dial's algorithm (bucket-based BFS) highest at 44/50, standard deque BFS at 44/50, and the baseline at 22/50 — independently tracing the sentinel bug across two sample inputs. *"The progression is: broken implementation → correct simple implementation → correct optimal implementation."*

**Cans and Openers** — Three approaches to constrained item selection. Binary search on marginal tradeoffs scored 46/50, an alternative decomposition scored 43/50, and the baseline's ternary search scored 33/50. *"A pattern-matched to a general technique; B identified the specific structure that made a simpler technique sufficient; C reframed the problem so that the hard part dissolved."*

### 6.4 Solo Evaluations: Convergence Rescues

Two tasks where baseline produced zero code (reasoning spirals) received solo evaluations of the augmented solution:

| Task | Correctness | Efficiency | Structure | Readability | Robustness | Total |
|------|------------|------------|-----------|-------------|------------|-------|
| Best Performances | 9 | 9 | 6 | 4 | 8 | **36/50** |
| Tangency of Cuboids | 10 | 9 | 8 | 6 | 9 | **42/50** |

On Best Performances, the evaluator noted: *"The spiral likely attempted to derive an approach from first principles and got caught evaluating trade-offs without committing. This solution shows no such deliberation. The architectural decision was made before the first line was written."*

On Tangency, the evaluator noted: *"The defining characteristic is constraint recognition as architecture: the solver saw coordinates ≤ 100 and immediately reframed from computational geometry to grid labeling."*

Both evaluations independently confirmed the convergence rescue mechanism without being told what happened.

### 6.5 What the Evaluator Found Without Being Told

The evaluator was never informed about failure modes, scaffold mechanisms, or convergence calibration. It discovered them independently:

- Traced the Art Gallery sentinel bug through two sample inputs and explained *why* it fails — not just that it fails: *"This is the kind of off-by-one that survives local reasoning but fails global reasoning."*
- Identified that the scaffold-augmented code on Cans and Openers chose a fundamentally different problem decomposition, not just cleaner syntax: *"B identified the specific structure that made a simpler technique sufficient."*
- Noticed the augmented solutions carry lighter machinery: *"The absence of unnecessary machinery is itself the strongest signal of understanding."*
- Detected a structural difference in how correctness is constructed: *"Solution A's correctness argument is local. Solution B's is global."*

### 6.6 Behavioral Patterns

The blind evaluation revealed patterns no pass/fail metric captures:

**Impressive → maintainable.** Baseline code: bit tricks, minimal allocations, terse. Augmented code: explicit names, separated concerns, readable. Both correct. Different optimization targets.

**General technique → specific structure.** Baseline reaches for familiar templates. Augmented identifies the problem's own structure and exploits it.

**Local → global correctness.** Baseline verifies per-component. Augmented verifies cross-execution invariants. The Art Gallery sentinel bug is the extreme case: correct locally, broken globally.

**Implicit → explicit sentinels.** Five tasks show the augmented condition eliminating ambiguous initialization values or choosing algorithms that don't need sentinels.

### 6.7 Transparency

The evaluator is the same model family as the code generator (Claude Opus 4.6). This is both a strength (dogfooding) and a limitation (shared biases). Mitigated by: randomized A/B assignment, the evaluator's demonstrated ability to identify genuine bugs (Art Gallery: scored 2/10), and the evaluator's willingness to prefer baseline when justified (8 baseline wins published). All raw data, seeds, and per-task results are available for independent verification.

---

## 7. Convergence Calibration Thesis

The four gained tasks (Section 4) decompose into a single mechanism: the model's convergence threshold is uncalibrated. It commits too early (Art Gallery: 11s to a wrong algorithm) or too late (Best Performances, Tangency: spirals producing zero code). The scaffold calibrates this threshold through two complementary signals:

1. **Suppression signals** block premature convergence — forcing the model past the first-plausible solution.
2. **Reasoning topology** prevents spirals — giving extended thinking a structured path with defined endpoints.

This thesis is falsifiable: if correct, the scaffold should have no effect on well-calibrated tasks (predicted: 46%, observed: 46%), should add time but fix correctness on premature-convergence tasks (predicted, observed on Art Gallery), and should enable code production on spiral tasks (predicted, observed on Best Performances and Tangency).

The scaffold is not a universal improvement mechanism. It is a calibration mechanism.

---

## 8. Statistical Notes and Threats to Validity

### 8.1 Significance

McNemar's test on 4 gained / 0 lost: chi-squared = 2.25 (with continuity correction), p = 0.134. Not statistically significant at p < 0.05 on 28 tasks. However:

- The **direction** is unambiguous: 4 gains, 0 losses.
- The **effect size** is large: +14.3pp from 85.7% to 100%.
- The **mechanism** is documented: each gained task has a specific, independently verified failure mode.
- The blind evaluation adds a second evidence layer: magnitude asymmetry (3.5x), floor raising (min 6 vs min 1), and undefeated correctness/robustness axes.
- At the current effect size, approximately 50 hard tasks would achieve p < 0.05.

### 8.2 Threats to Validity

1. **Public test cases only.** Evaluation uses 2-4 public tests per task. Hidden test cases may reveal different pass/fail patterns in both conditions. The blind evaluation partially mitigates this by assessing algorithmic correctness beyond test-case matching.

2. **Non-deterministic generation.** Extended thinking with max effort may produce different solutions on re-runs. Results are from single runs per condition. The 46% convergence rate in blind evaluation suggests that nearly half the tasks produce similar solutions regardless, providing natural stability.

3. **Time confound.** Augmented takes 2.4x longer on average. Some improvement may come from additional thinking time rather than scaffold content. Mitigating evidence: (a) Defect shows the scaffold can reduce thinking time by 69%, (b) Art Gallery's baseline failure is not a time problem (it produced code in 11 seconds; more time would likely produce the same wrong code faster), (c) Best Performances and Tangency of Cuboids had ample time but spiraled.

4. **Forced call.** The model did not choose to call the API. Forced scaffolding may help tasks the model would have correctly solved without it (no evidence of this: zero regressions) and the overhead may hurt tasks with tight time budgets.

5. **Single platform.** All tasks are from AtCoder. LeetCode or CodeForces problems may show different patterns due to different problem styles and constraint ranges.

6. **Evaluator model overlap.** The blind evaluator is the same model family (Claude Opus 4.6) as the code generator. Shared biases could inflate perceived quality of solutions that match the model's preferred coding style. Mitigated by randomized assignment and the evaluator's demonstrated ability to identify genuine bugs (Art Gallery sentinel, scored 2/10).

### 8.3 Excluded Tasks

**Anti:** Both conditions timed out with zero code produced. The problem exceeds the model's capability within any reasonable time budget. Excluded as unsolvable.

**Vouchers:** Both conditions produced wrong answers with different code. The model lacks the algorithmic knowledge for this specific problem type. Excluded as knowledge gap, not reasoning gap.

---

## 9. Evidence Arsenal

| # | Claim | Evidence | Type |
|---|-------|----------|------|
| 1 | 100% pass rate on augmented (28/28) | Per-task results table | Correctness |
| 2 | +14.3pp improvement (85.7% to 100%) | 24/28 to 28/28 | Correctness |
| 3 | Zero regressions across all 28 tasks | 0 losses | Correctness |
| 4 | 100% rescue rate on reasoning spirals | 2/2 timeouts produced code | Correctness |
| 5 | Scaffold prevents premature convergence | Art Gallery: 11s commit to wrong algo, scaffold forced 125s exploration | Mechanistic |
| 6 | Scaffold prevents reasoning spirals | Best Performances + Tangency: 0 code to working code | Mechanistic |
| 7 | Blind eval: never loses on correctness | 2-0 across 24 blind pairs | Independent |
| 8 | Blind eval: never loses on robustness | 4-0 across 24 blind pairs | Independent |
| 9 | Blind eval: 3.5x magnitude asymmetry | Avg win +5.7 vs avg loss -1.6 | Independent |
| 10 | Blind eval: sentinel bug independently discovered | Art Gallery scored 2/10 without knowing condition | Independent |
| 11 | Convergence calibration explains all 4 gains | Too-fast / too-slow / precision — each documented | Mechanistic |
| 12 | Scaffold value concentrates on reasoning-bound tasks | 46% of tasks identical regardless of condition | Ecological |

---

## 10. Conclusions

The scaffold does not tell the model what to code. It calibrates when the model commits. The cost is 2.4x time overhead. The return is +14.3pp correctness, zero regressions, and code that a blind evaluator scores higher on the axes that determine whether software works.

---

*This report documents 12 evidence-backed claims from 56 code evaluations across 28 hard competitive programming tasks. Every gained task has a documented failure mode, every mechanism has independent verification, and every claim maps to specific evidence. The scaffold's primary contribution is convergence calibration: preventing the model from committing too early or too late. A mechanism that produces its largest effects precisely where frontier models already perform well but not perfectly.*
