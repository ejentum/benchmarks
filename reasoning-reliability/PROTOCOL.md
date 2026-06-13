# Protocol

Each run is one stateless agent given the task spec and one arm's instructions.
The spec (`tasks/<task>/SPEC.md`) is byte-identical across arms; the agent reads
only the spec, writes a single solution file, and never sees the oracle. The
manipulated variable is the reasoning-layer block below.

## Arms

### raw
> Solve it using your own engineering judgment. Use NO external tools, MCP
> servers, or CLIs.

### prompt (framing words only, no tools)
> Use NO external tools. Before writing code, frame the problem deliberately:
> tasks like this often admit more than one reading, and the first obvious
> approach is not always the one the objective requires. Locate yourself between
> the competing readings of what is really being optimized. Do not collapse onto
> the default method just because it is natural; ask whether it actually achieves
> the stated objective across ALL inputs or only the easy ones. Hold the obvious
> approach and its alternative in view together, decide which the objective truly
> demands, then implement that one.

This arm exists to attribute the harness's contribution precisely: it separates
generic framing from the task-matched operation and the correct, pre-named
structural criterion that the harness retrieves.

### tooled (harness retrieved and consulted)
> Before writing code, run a framing phase once: (1) superposition (CLI) to get a
> two-pole axis and locate yourself between the poles; (2) adaptive-code (MCP) for
> the task-matched cognitive operation; absorb both. Then implement.

### tooled_proper (harness reasoned through)
Same retrieval as `tooled`, but the operation is applied, not skimmed:
> (a) SUPPRESS GATES: restate each `Suppress:` signal as a concrete failure mode
> you will actively block in this task; keep them as a checklist.
> (b) WALK THE TOPOLOGY: treat each reasoning-topology node (S-steps, gates,
> meta-nodes) as an explicit reasoning step, written out node by node.
> (c) RUN THE PROCEDURE as your actual procedure.
> Then implement, and before finalizing, state the `[FALSIFICATION TEST]` from the
> operation, apply it to your draft, and check the draft against the superposition
> far pole. Only finalize if it passes.

The `tooled` vs `tooled_proper` split exists because an operation that arrives as
a tool result is content the model can skim; applying it as an instruction
(walk the topology, run the falsification test) is what makes the reasoning layer
load-bearing instead of decorative.

## Models

Run with the same protocol across models to confirm the reasoning discipline holds
with capability. Recorded here: Sonnet 4.6 and Opus 4.8, where it reproduced on
both. The protocol extends to additional models with no changes.

## Sampling

k independent runs per arm (k=6 for word_wrap, k=5 for apply_ops here). Each run
is graded `PASS` only if correct on all oracle categories. Report the per-arm
pass rate; do not optionally stop or cherry-pick runs.
