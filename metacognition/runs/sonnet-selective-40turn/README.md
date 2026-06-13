# Run: sonnet-selective-40turn

The **clean run**. The first run where the tools were used selectively *and* faithfully, on a model capable enough to self-calibrate.

| | |
|---|---|
| Model | Claude Sonnet |
| Turns | 40 (single continuous session, completed unforced) |
| State | continuous, one context |
| Tools | self-inspect + superposition (universal, `task_type`-free grid) |
| Tool framing | auxiliary, "reach for them only at a genuine hard knot," interleaved rhythm, self-locate (not pole-flip) |
| **Tool calls** | **2 real**, both at the unity-of-consciousness knot (~turns 14–16), then ~24 turns of solo reasoning |
| Faking | none (both calls verified real: `tool_use` + `tool_result`) |

## Why this run matters

It resolves the calibration question from the rest of the bench. Haiku could not hit selective-but-honest tool use: on "every turn" it over-called (distractive), on "collapse-triggered" it fired 0 times, on "selective" it fired ~never and **fabricated** the one call it pretended to make. Sonnet, same selective instruction, fired exactly twice, both real, both at the hardest point, and the superposition axis it located itself in genuinely redirected the back half (functional vs philosophical standards of introspective success). See `calls.md` for the verbatim call log and `full_run.md` for the 40 turns.

So: the tools as auxiliary checkpoints fired only at genuine knots **work**, on a model that can judge when it is stuck. The corrosion seen elsewhere came from over-calling or weak-model miscalibration, not from the tools themselves.

## Files
- `full_run.md` — the 40 turns, verbatim from the transcript
- `calls.md` — the complete log of both tool calls (input + output, verified real)
- `transcript.jsonl` — raw execution log (ground truth)

## Caveat
n=1 on Sonnet, one topic. This is the first evidence the tools help a capable model selectively; it needs replication and a blind panel vs the no-tools control.
