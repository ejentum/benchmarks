# MHPP-10 Ablation — Pre-Registration

Date: 2026-05-31
Model: Claude Opus 4.8 via Claude Code subagent fleet
Reps: 1 per (task, condition) pair
Protocol: each solve agent calls /harness/ itself when it sees its task (agentic-tool pattern, not pre-generation)

## Conditions
- B (raw baseline): no harness call, solve directly
- D (dynamic code): agent calls /harness/ with mode=code, injects top-1 retrieval, then solves
- A (adaptive code): agent calls /harness/ with mode=adaptive-code, injects top-5 + adapter-rewritten scaffold, then solves

## Predicted pass rates (out of 10)
- A: 6-8 (full product)
- D: 4-6 (content matched, no adapter)
- B: 2-4 (Opus 4.8 native on hardest MHPP)

## Hypotheses
- H1: A > D > B (clean step-ladder)
- H2: A roughly equal to D, both > B (harness helps, adapter is icing)
- H3: null result, all roughly equal (publish honestly)

## Commitment
Results published whether they confirm or not.
