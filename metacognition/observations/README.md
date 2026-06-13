# Observations

This is where the findings go, **after** a thorough pass over the data in
[`../runs/`](../runs/). It is intentionally empty of conclusions right now. The
repo ships the instrument, the data, and the proof first; the reading comes
second and must be earned from the transcript.

## What an observation pass has to do here

1. **Read the full chain, not the summary.** Work from `full_loop.md` /
   `full_loop.jsonl` (verbatim, transcript-derived), not only the model's
   self-reported `journal.jsonl`.
2. **Separate the model's reasoning from the tools' fingerprint.** Superposition's
   two-pole format and self-inspect's question set shape the wording. A finding
   has to survive that subtraction.
3. **Test deepening against fixation.** Did turn 40 genuinely depend on turns
   1-39, or did the model settle into a self-invented vocabulary and reason
   inside it? Cite turn numbers as evidence either way.
4. **Mark every claim's level.** Process vs correctness. This benchmark can speak
   to what the loop *did to the reasoning*; it cannot speak to whether the
   model's philosophy is true.
5. **Name what is not yet here.** A control arm (no tools / unenforced),
   cross-model and cross-topic runs. State the limits with the findings.

## Format (when written)

Each finding: a one-line claim, the turns/quotes that ground it, the level it
operates at (process / structure / artifact-of-tooling), and what would falsify
it. No metric appears in the public README until it is substantiated here.

> Status: pending. Nothing in this directory is a published result yet.
