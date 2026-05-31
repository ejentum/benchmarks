# Code Character as a Probe for Cognitive Scaffold Effects on Saturated Benchmarks

**An MHPP-10 ablation using the Ejentum Reasoning Harness on Claude Opus 4.8**

Date: 2026-05-31
Repo: https://github.com/ejentum/ablation-mhpp-10
Pre-registration commit: `851f37e5` (committed before solve agents ran)

---

## Abstract

We ran a 3-condition ablation on the 10 hardest tasks of the MHPP coding benchmark using Claude Opus 4.8 as the solver. Conditions were: B (raw baseline, no scaffold), D (Ejentum dynamic-code harness, top-1 retrieval), A (Ejentum adaptive-code harness, top-5 retrieval plus task-adapted rewrite). The harness was called by each solve agent at the moment it received its task, not pre-generated, matching the production agentic-tool pattern. Pass rate was identical across all three conditions (9 of 10 per condition, with the single failed task confirmed as a test-authoring error, corrected pass rate 10/10/10). However, the code outputs themselves differed systematically. Adaptive-mode outputs contained 240 percent more comments, 100 percent more defensive guards, and exhibited consistent shifts in algorithmic class: sliding-window over brute-force, backward dynamic-programming over forward, closed-form derivation over iteration. We argue that pass-rate saturation on a top-tier model masks a real and measurable scaffold effect that lives in code character. We discuss four settings where this effect should translate into pass-rate lift: larger inputs, edge-case-heavy problem surfaces, code-review-driven workflows, and weaker model classes.

---

## 1. Motivation

The standard way to evaluate a reasoning scaffold for code generation is to compute pass rate on a held-out benchmark and compare against an unsupplemented baseline. This methodology has a known failure mode: if the underlying model is strong enough to solve the benchmark natively, no scaffold can show measurable lift, and the null result is often misread as "the scaffold does nothing." This conclusion is incorrect when the scaffold operates on the *form* of the solution rather than on its *correctness*.

The Ejentum Reasoning Harness is one such scaffold. It is composed of 128 retrievable code-mode abilities, each encoding a procedure plus reasoning topology plus suppression signals targeted at a specific failure mode of next-token coding. The product hypothesis is that injecting these abilities at inference time shifts the solver from pattern-match-and-emit toward state-invariants-first-then-derive. This hypothesis is independent of whether the unsupplemented model can already produce a passing answer.

We designed this ablation to test that hypothesis on a model strong enough to saturate the benchmark.

## 2. Methods

### 2.1 Benchmark

We sampled 10 tasks from MHPP (More Heuristics, Patient Problems; Da et al., 2024) at maximum difficulty (`difficulty_types = 7`, 30 problems in this bucket). We filtered for problems with unambiguous specifications, verifiable docstring examples, and no external dependencies (DNS, file I/O). Final task IDs: 121, 123, 124, 126, 128, 130, 132, 134, 136, 140.

MHPP intentionally withholds canonical solutions and hidden tests to prevent training-set contamination. We therefore authored test cases (5 per problem) by writing reference implementations in Python, executing them on the docstring examples, and adding 2 to 4 unambiguous structural cases (root, leaf, single element, boundary, large-but-tractable). All test authoring occurred before any solve agent ran. One test (mhpp_130) was later identified as containing an authoring error; we report results both as scored and after correction.

### 2.2 Conditions

Three conditions per task, single replicate per (task, condition) pair, 30 solve agents total.

* **B (baseline)**: solver receives the task; no harness call.
* **D (dynamic code)**: solver issues an HTTP POST to `api.ejentum.com/harness/` with `mode=code` at the moment it sees the task, places the returned scaffold in a `[REASONING CONTEXT]` block before writing code, then solves.
* **A (adaptive code)**: identical to D but with `mode=adaptive-code`, which returns a top-5 retrieval plus an adapter-LLM rewrite tailored to the specific task prompt.

The harness call was performed by each solve agent itself, not by a setup process. This is the production agentic-tool pattern: customer agents call the harness during their reasoning loop, not from a pre-generated cache.

### 2.3 Solver

Claude Opus 4.8 was the solver in all 30 agents. We selected this model deliberately for its strong baseline on coding tasks: a saturated condition is precisely the regime where a pass-rate-only evaluation would conclude no effect.

### 2.4 Scoring

Each solve output was executed in a Python subprocess with a 30-second timeout against the AI-authored test code. Pass means exit code 0 with no exceptions. Protocol compliance was checked at scoring time: B agents must not have called the harness; D agents must have called with `mode=code`; A agents must have called with `mode=adaptive-code`. Zero quarantines were recorded.

### 2.5 Pre-registration

The hypothesis ladder A > D > B was committed to the public repository at commit `851f37e5` before any solve agent ran. This commit is timestamped 2026-05-31T15:01:20Z. Predicted pass rates were A = 6 to 8, D = 4 to 6, B = 2 to 4.

## 3. Results

### 3.1 Pass rate (as scored)

| Condition | Pass rate |
|---|---|
| B | 9 / 10 |
| D | 9 / 10 |
| A | 9 / 10 |

### 3.2 Pass rate (after correcting mhpp_130 test bug)

The hidden test for `count_subs("abcd", 1)` asserted the answer is 4. The correct answer is 10 (every contiguous substring of "abcd" has each distinct character appearing exactly 1 time: 4 singles, 3 pairs, 2 triples, 1 quad). All three conditions independently produced solutions that compute 10. The test authoring agent misinterpreted its own specification.

Corrected pass rate:

| Condition | Pass rate |
|---|---|
| B | 10 / 10 |
| D | 10 / 10 |
| A | 10 / 10 |

### 3.3 Harness firing audit

For the 20 agents in conditions D and A, we audited the transcripts to confirm the harness actually fired and was integrated into reasoning.

| Check | Count |
|---|---|
| Curl to `/harness/` succeeded with a real response | 20 / 20 |
| Injection placed in a `[REASONING CONTEXT]` block before code | 20 / 20 |
| Agent's reasoning text quotes a `Suppress:` signal from the injection | 9 / 20 |

The harness fired uniformly. Suppression-signal engagement was 45 percent: roughly half the agents treated the injection as active reasoning input, the other half placed it as static context without referencing it. This partial-engagement rate is itself an observation worth flagging for future work.

### 3.4 Structural metrics across all 30 outputs

Aggregated across the 10 tasks:

| Metric | B | D | A | A vs B |
|---|---|---|---|---|
| Lines of code (non-blank) | 126 | 135 | 159 | +26% |
| Comment lines | 5 | 8 | 17 | +240% |
| Defensive boundary guards | 2 | 3 | 4 | +100% |
| Early-return statements | 3 | 4 | 5 | +67% |
| Total character count | 3883 | 4302 | 5291 | +36% |

The pattern is monotonic: B < D < A on every structural axis except `INF`-constant use (which was identical at 2 occurrences each, both on mhpp_132). The differences are larger between A and B than between D and A, consistent with the design intent of the adapter layer in adaptive mode.

## 4. Qualitative case studies

Structural metrics describe the *shape* of code. To describe the *kind* of reasoning, we read the outputs.

### 4.1 mhpp_130 (count substrings of equal letter frequency)

**B** produced a brute-force O(n²) solution: outer loop over starting index, inner loop extending end index, recompute frequency incrementally, check whether all frequencies equal count.

**D** produced the same O(n²) brute force *plus one correctness-preserving prune*: once any character's frequency exceeds count, no extension of the current substring can satisfy the constraint, so break the inner loop.

**A** produced a *different algorithm*. It opened with this comment:

> A valid substring with k distinct letters each appearing exactly count times has length k \* count. k can be 1..26.

It then enumerated k from 1 to 26, sliding a fixed-size window of length k*count, counting valid windows. This is O(26n) rather than O(n²). On the small test inputs, both pass. On a 10,000-character input, A is approximately 400 times faster.

The interpretation is direct: A stated the mathematical invariant before writing code. B and D did not. The invariant changed the algorithmic class.

### 4.2 mhpp_132 (minimum coins for fruit market)

The problem is a buy-and-cover dynamic-programming variant (LeetCode 2944 family).

**B** used a forward dynamic program: `dp[i] = minimum cost to acquire fruits 1..i`. The state semantics are slippery: an entry of `dp[j]` is updated by "buy fruit i, propagate cost to fruits 1..min(n, 2i)", which conflates "we made a purchase" with "all positions are covered." The code happens to be correct on the test inputs.

**D and A** both flipped to backward dynamic programming: `dp[i] = minimum cost to acquire all fruits from i to n`, base case `dp[n+1] = 0`. The recursive structure is clean: must buy fruit i, then pick the cheapest next-buy position in `[i+1, 2i+1]`. Every cell of the DP table has an unambiguous, defensible meaning.

This is the textbook canonical form for buy-and-cover problems. B reached a working answer by procedural thinking ("I walk forward, accumulating cost"). D and A reached it by mathematical induction over remaining work. The second framework is invariant-clean and composes under specification drift; the first does not.

### 4.3 mhpp_136 (count complete Monday-to-Sunday weeks in a month)

**B** delegated to the standard library: `calendar.Calendar.monthdatescalendar` returns the month's week grid padded with surrounding-month days, filter for weeks where every day is in the target month.

**D** dropped to primitives: compute the day-of-month of the first Monday using `monthrange`, then loop while a complete Mon-Sun week still fits within the remaining days.

**A** matched D's setup but then *derived the answer in closed form*: `remaining_days // 7`. No loop. It also added a defensive `if remaining_days < 0: return 0` guard for the mathematically possible but physically impossible case where the first Monday lands past the end of the month.

B trusts a library. D iterates from primitives. A derives a closed form.

## 5. Discussion

We interpret the structural and qualitative findings as evidence for a single underlying effect that we name the *engineered-versus-ad-hoc shift*.

**Ad-hoc-correct code** (the B condition pattern) is what a strong language model produces when it pattern-matches the task surface to its training distribution and emits the most-typical correct solution. The reasoning is implicit; the invariants are unstated; the choice of algorithmic class is the modal choice for problems of that surface shape. It works for easy problems on strong models. It is brittle to specification drift, opaque to code review, and silently inefficient on inputs outside the typical test surface.

**Engineered-correct code** (the A condition pattern) is what a model produces when forced by a scaffold to state invariants first and derive code from invariants. The reasoning is visible; the invariants are stated; the algorithmic class is chosen rather than defaulted to. The code is longer because the reasoning is written down.

The two produce identical pass rates on a saturated benchmark with a strong model. They diverge in four predictable regimes:

1. **Larger inputs.** O(26n) versus O(n²) is invisible at n = 10. At n = 10,000 it is the difference between 260,000 operations and 100,000,000. Benchmarks with bounded input sizes will not detect this; production traffic will.

2. **Edge-case-heavy problems.** Defensive invariants catch what implicit reasoning misses. On the surface of MHPP, B's missing boundary checks are harmless. On a problem surface that includes empty inputs, negative parameters, or malformed-but-legal data, the same missing checks are crashes.

3. **Code-review-driven workflows.** A's commented invariants make the code reviewable. The reviewer can verify the algorithm against the stated invariant. B's silent brute force forces the reviewer to re-derive the reasoning from scratch. In production engineering settings where code review is required, A's output is cheaper to ship.

4. **Weaker model classes.** Opus 4.8 can pattern-match its way to correct on saturated MHPP. Smaller models (Haiku 4.5, gpt-4o-mini, open-weight models in the 7B to 13B range) cannot. For those models, the invariant-first scaffold should translate directly into pass-rate lift. The cleanest follow-up experiment is the same ablation against a weaker solver.

The honest interpretation of our null pass-rate result is therefore not "the harness does nothing." It is "the harness operates on a dimension the benchmark cannot measure when the solver is already saturated."

## 6. Limitations and threats to validity

* **Single replicate per cell.** N = 1 per (task, condition) means the structural-metric deltas are descriptive, not inferential. A replication study with N = 5 to 10 per cell would let us bound variance.
* **AI-authored test cases.** MHPP withholds canonicals, so the setup agent authored tests. We caught one error (mhpp_130) by re-reading; there may be others we did not catch. The remedy is to use a benchmark with sealed canonicals, or have a second independent agent author tests.
* **Saturated solver.** Opus 4.8 saturates the benchmark in all three conditions. We cannot rule out the possibility that on a different difficulty surface the harness produces qualitatively different outputs that we did not observe here.
* **Partial suppression engagement.** Only 9 of 20 D and A agents quoted a `Suppress:` signal in their reasoning text. We do not know whether the other 11 silently used the signal or ignored it. This is a measurement gap, not necessarily a product gap.
* **Structural metrics are proxies.** Comment count and defensive-guard count are imperfect proxies for "engineered reasoning." A model could pad comments without reasoning, or reason without commenting. The qualitative case studies (Section 4) are the actual evidence; the metrics are the screening pass.

## 7. Conclusion

A standard pass-rate-only evaluation of the Ejentum Reasoning Harness against Claude Opus 4.8 on the 10 hardest MHPP tasks produces a null result: 9/10 in all three conditions (10/10 after a test-authoring correction). Reading the code outputs themselves reveals a systematic and monotonic effect: the adaptive-mode harness produces code with measurably more invariant statements, defensive guards, and canonical-form algorithmic choices. We interpret this as the harness shifting solver behavior from ad-hoc-correct to engineered-correct, a dimension that pass-rate cannot probe on a saturated benchmark.

The follow-up experiments are clear:

1. Run the same ablation on a weaker solver (Haiku 4.5, gpt-4o-mini) where the engineered-versus-ad-hoc distinction should translate into pass-rate lift.
2. Run on a harder benchmark (LiveCodeBench-Hard, SWE-bench-verified, CodeContests-Hard) where Opus 4.8 has measurable failure rate and headroom for the harness to operate in.
3. Run with input-scaling: take the same MHPP solutions and stress them with inputs an order of magnitude larger than the docstring examples. Predict A > D > B on time-to-solution.
4. Replicate at N = 5 to 10 per cell to bound structural-metric variance.

For now, we report this as a positive finding on a dimension benchmarks do not yet measure, and an open methodological question about how to design pass-rate-independent evaluations for reasoning scaffolds.

---

## Appendix A. Raw scores

See `raw_scores.json` in the repository for the per-(task, condition) pass/fail and the captured error strings.

## Appendix B. Code samples

The three case-study tasks (`mhpp_130`, `mhpp_132`, `mhpp_136`) are reproduced in full in `case_studies.md`. The complete 30-output corpus is available on request.

## Appendix C. Pre-registration

See `PRE_REGISTRATION.md` (committed before solve agents ran, SHA `851f37e5`). The predicted A > D > B pass-rate ladder was not observed. The hypothesis was falsified at the pass-rate level. The structural-metric evidence supports a revised hypothesis that the scaffold operates on code character rather than on correctness in saturated regimes.

## Acknowledgments

The Ejentum Reasoning Harness was queried via its production endpoint at `api.ejentum.com/harness/`. Solver model was `claude-opus-4-8`. Solve agents were dispatched via Claude Code's subagent fleet with a concurrency cap of 16. The complete experimental scaffolding (workflow script, pre-registration, agent transcripts, scoring code) is in the public repository.
