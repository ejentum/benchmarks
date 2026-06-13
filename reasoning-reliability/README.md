# Reasoning Reliability Benchmark

A benchmark for the **reliability layer** of an agentic runtime. It measures whether
an agent's reasoning is explicit, justified, guard-checked, and auditable, the
properties a runtime needs to catch a wrong step before the next step builds on it.

Most coding benchmarks ask "is the final answer right?" That question matters, but
it is not where agentic systems fail in production. They fail silently: a correct
step and a confidently-wrong step present the same surface ("done, tests pass"), so
a wrong decision early propagates downstream with no human in the loop to catch it.
The defense is not more capability. It is making each reasoning step inspectable and
checkable. This benchmark measures exactly that, and shows what the Ejentum harness
installs on top of a strong model.

## What the harness does here

Across frame-trap coding tasks on **Sonnet 4.6** and **Opus 4.8**, applying the
harness produces, reliably and reproducibly:

1. **Correct targeting on every task.** The retrieved operation named the *actual*
   failure mode each time: the greedy-choice property (`word_wrap`), atomic
   TTL-expiry-under-lock / shared-mutable-without-lock (the cache task), the
   no-rescan adversarial case (`apply_ops`). The engine fits the right cognitive
   operation to the task, not a generic one.

2. **Explicit, auditable reasoning.** The harnessed runs *name the rejected frame*
   ("greedy would fail the forced-singles case"), *justify the algorithm class*
   ("the problem lacks the greedy-choice property, so DP is the justified class"),
   and *pre-commit to the guard* (`Suppress: greedy-without-property`) before
   writing code, then check the draft against it. The reasoning is legible and
   challengeable by construction, which is what makes it auditable at runtime.

3. **The correct, pre-named structural criterion.** The harness hands the agent the
   precise concept the task turns on (greedy-choice property, TOCTOU, no-rescan)
   plus the falsification test that checks it. The agent reasons with the right
   frame instead of having to surface it under pressure.

4. **A verification discipline.** Every harnessed run executed a structural
   falsification test against an independent reference before finalizing.

5. **It holds on the frontier model.** The discipline carried fully onto Opus 4.8,
   not just Sonnet. The reliability layer is not fragile to model strength.

6. **It is added at negligible, harmless cost.** Every harnessed solution passed the
   deterministic oracle, verified correct on all discriminating, basic, and edge
   cases. The auditability comes with no correctness regression: a small, bounded
   reasoning overhead, full task correctness retained.

## Why a reliability layer is the right thing to measure

In an autonomous, multi-step runtime there is no human reading every step.
Explicit forks, justified classes, and pre-declared guards turn an opaque
generation into a *claim* a cheap verifier, a monitor, or an audit can act on:

- **Naming the fork** instruments the decision, the runtime gets a point it can log,
  gate, or escalate. A silent correct choice gives a monitor nothing to watch.
- **Justifying the class** carries the reasoning's own cheap check ("is the
  greedy-choice property satisfied?"), which a lightweight verifier can validate far
  cheaper than re-solving the task.
- **Pre-committing the guard** is a pre-registered invariant on the reasoning, the
  assertion statement that agent reasoning has never had, and the only verification
  that cannot be rationalized after the answer is chosen.

Those are the primitives every reliability discipline is built on: observability,
cheap verification, pre-registered invariants, audit trails. The harness installs
them into the run.

## Design

1. **Frame-trap tasks.** Each task has a tempting *wrong frame* (greedy line-filling,
   or a sequential reading) and a correct frame (a global DP, or a single-pass
   reading). The wrong frame is verified to fail the oracle, so the auditability the
   harness adds is exercised against a real fork, not a strawman.
2. **Deterministic oracle (source of truth).** Grading is exact-match against a
   reference solution on a frozen vector set. No LLM judge anywhere. Each oracle
   self-validates (`python tasks/<task>/oracle.py`) that the wrong frame fails the
   discriminating vectors and that the reference is brute-force-correct.
3. **Arms.** The spec is byte-identical across arms; only the reasoning layer differs
   (`raw`, `prompt`, `tooled`, `tooled_proper`). See `PROTOCOL.md`.

## Tasks

| task | the fork | correct frame | the structural criterion the harness names |
|---|---|---|---|
| `word_wrap` | greedy vs global | DP (min sum of cubed trailing space) | greedy-choice property |
| `apply_ops` | sequential vs single-pass | single pass over original, no re-scan | no-rescan / list-order priority |

## Run it

```
python run.py tasks/word_wrap results/word_wrap_sonnet
python run.py tasks/word_wrap results/word_wrap_opus
python run.py tasks/apply_ops results/apply_ops_sonnet
```

Every run across every arm and model is verified correct by the oracle (see
`RESULTS.md`); the benchmark's signal is the reasoning the harness adds on top.

## Layout

```
README.md          this file
PROTOCOL.md        exact arm definitions and the harness application protocol
RESULTS.md         oracle pass results, trap-validity numbers, reasoning-trace evidence
run.py             deterministic grader (no LLM)
tasks/<task>/SPEC.md     the agent-facing spec (identical across arms)
tasks/<task>/oracle.py   the deterministic oracle (source of truth, self-validating)
results/<task>_<model>/  submitted solutions, one file per run, as evidence
```

Extends naturally to additional models and tasks.
