# Correction (2026-06-01)

## What was wrong

The initial publication of this benchmark on 2026-06-01 reported:

> B = 4/15, D = 4/15, A = 2/15. The adaptive arm regressed below bare baseline.

That headline was incorrect. The judge agent's own per-item judgments (preserved in the agent transcript) show:

> B = 4/15, D = 5/15, A = 5/15. Both harness arms produced a +1 question lift over baseline.

## How the error happened

The benchmark uses a single LLM judge agent (Claude Opus 4.8) that grades all 45 submissions for semantic equivalence against the canonical answers, with X/Y/Z anonymization rotated per question. The judge agent returns a structured output containing two fields that should agree:

1. `judgments` — an array of 45 per-item entries, each marked `passed: true/false`
2. `pass_rate_B`, `pass_rate_D`, `pass_rate_A` — aggregate string fields like `"5/15"`

The judge agent's `judgments` array (the actual ground-truth data) is correct. Its `pass_rate_*` aggregate fields were computed inconsistently with its own per-item judgments:

- `judgments` array counted: B=4 passes, D=5 passes, A=5 passes
- `pass_rate_*` fields reported: B=4/15, D=4/15, A=2/15

The downstream Writeup phase consumed the `pass_rate_*` fields rather than the `judgments` array, propagating the error into RESULTS.md, chart.svg, raw_scores.json, the index repo, the root README row, and the CHANGELOG entry.

## What got corrected

The patched files now compute aggregate pass rates directly from the per-item `judgments` array preserved in the agent transcript. `raw_scores.json` now contains the full 45-item per-item data so any future reader can re-verify the aggregates independently.

The per-item data was never wrong. Only the aggregate computation downstream of it was wrong. The original judge transcript is preserved verbatim in the workflow's subagent log at `subagents/workflows/wf_8f079962-1b8/agent-a0bde3c6d9409c537.jsonl` (transcript path on the run machine; the per-item content is reproduced in this repo's `raw_scores.json`).

## Methodological implication

The judge agent's `pass_rate_*` aggregate fields are no longer trusted. Future benchmark runs should either:

1. Compute aggregates downstream from the per-item array, not trust agent-emitted aggregate fields, OR
2. Run a separate verification pass that re-tallies the per-item judgments and reports any discrepancy with the agent's aggregate

This benchmark's RESULTS.md, chart.svg, raw_scores.json, the root README row in `ejentum/benchmarks`, and the CHANGELOG entry have all been patched.

## Why this is in version control

The original incorrect commit history is preserved in the git log of this repo. Any reader auditing the timestamps can verify:

- Pre-registration committed at `e45aeac5` before any solver ran
- Initial (incorrect) results committed shortly after the workflow's writeup phase completed
- This correction committed on 2026-06-01

The correction does not alter the experimental data. It only corrects the arithmetic on top of that data.
