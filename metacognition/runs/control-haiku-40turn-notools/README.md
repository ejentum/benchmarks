# Run: control-haiku-40turn-notools

The **control arm**. Identical to `stateful-haiku-40turn` in model (Claude Haiku 4.5), topic ("thinking about thinking"), length (40 turns), statefulness (one continuous mind), and journaling discipline. The **only** variable removed: the two tools. No superposition, no self-inspect, no forced divergence, no external doubt. Same seed question, same "build on every prior turn, cite earlier turns by number" rules. This isolates what the tools cause.

## Parameters

| | |
|---|---|
| Model | Claude Haiku 4.5 |
| Turns | 40 |
| State | continuous (one context, single agent, start to finish) |
| Tools | **none** (the only command run is the per-turn journal append) |
| Seed question | "What is actually happening when a mind examines its own thinking?" |

## Provenance (honest about how it was produced)

A weak model under-persists on a long *free-form* mandate. This control took three launches to get one clean single-agent run, and that fact is itself a result:

- `attempts/attempt1_stopped_at_5.journal.jsonl` — first launch **quit at turn 5** (wrote long essays, then stopped). The tools-on run, by contrast, completed 40 in one shot. The per-turn tool rhythm aids long-horizon persistence; remove it and the same model quits early.
- `attempts/attempt2_stitched_40.journal.jsonl` — re-threw the 5 prior turns at a fresh agent to continue 6-40; it reached 40, but across **two contexts** (stitched), so it is not one continuous mind. Kept as provenance only.
- `journal.jsonl` / `transcript.jsonl` — **the run used for the delta**: one fresh agent, all 40 turns in a single continuous context, under a hardened mandatory-completion prompt (concise turns + hard no-stop contract). Verified `turn` field is a clean 1..40.

The `journal.jsonl` was normalized from the agent's cp1252 dash output to valid UTF-8; the model's wording is otherwise untouched. `transcript.jsonl` is the raw single-agent execution log.

## What it showed (summary; full delta in `observations/`)

The control did **not** collapse: back-half content stayed flat (0.97 of front half vs the tools-on run's 0.77), and its forward questions did not degrade (1.10 vs 0.61). It reached the introspective bind **less** and **later** (9/40 turns from turn 8, vs 20/40 from the start). And it kept advancing to new substantive ground through turn 40, where the tools-on run turned inward and consumed itself. The tools do not deepen the thinking; they destabilize it. See `observations/2026-06-12-pass1-tools-on.md` (updated with the delta).
