# Run: stateful-haiku-40turn

A single continuous Claude Haiku 4.5 agent, 40 turns, one subject: *thinking about thinking*. One context the whole way, accumulating. Two tools, nothing else (no web, no other actions).

## Parameters

| | |
|---|---|
| Model | Claude Haiku 4.5 |
| Turns | 40 |
| State | continuous (one context, full memory of prior turns) |
| Tools | `superposition.py` (forced divergence, mandatory each turn), `self_inspect.py` (doubt, each turn) |
| Seed question | "What is actually happening when a mind examines its own thinking?" |
| Other tools / web | none |

## Tool calls (counted from the transcript, not self-reported)

- superposition.py: **40** (once per turn)
- self_inspect.py: **40** (once per turn)
- journal appends: 40, plus 2 setup commands (`ls`, `mkdir`). 122 Bash calls total.

## Verification

```sh
python ../../verify/verify_calls.py .
# self_inspect  re-run == logged: 40 ok, 0 mismatch
# superposition re-run == logged: 40 ok, 0 mismatch
# RESULT: ALL CALLS VERIFIED
```

All 80 tool calls re-run identically on their recorded inputs. The run is not fabricable.

## Files

| File | What it is |
|---|---|
| `transcript.jsonl` | the raw agent execution log. Ground truth. Every Bash call and its output. |
| `journal.jsonl` | the model's own per-turn summary (`claim, map, pole_assumed, pole_taken, reframe, metathought, answer, insight, next_question`). Self-reported. |
| `full_loop.jsonl` | reconstructed from the transcript: per turn, the model's three reasoning blocks + verbatim tool inputs/outputs + the journal object. |
| `full_loop.md` | `full_loop.jsonl` rendered for reading (lightly cleaned; model wording untouched). |
| `orchestration_prompt.txt` | the exact prompt that drove the run. |

## Shape of the run (for the observation pass, not a conclusion)

The model took the other pole all 40 turns, referenced its own earlier turns by number, and showed genuine self-reference about being mid-process (it notes how far in it is, that practice has "colonized" its freedom, that the journal cannot record the act of writing it). Whether that constitutes deepening or a closed self-invented vocabulary is what [`../../observations/`](../../observations/) must decide from this data. **No finding is asserted here.**

## Status

Data complete and verified. Observations pending. Not yet published.
