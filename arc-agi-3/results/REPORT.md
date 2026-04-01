# ARC-AGI-3 Benchmark: Baseline vs RA²R-Augmented

## Overall Results

| Metric | Baseline (A) | Augmented (B) | Delta |
|--------|-------------|---------------|-------|
| Mean RHAE | 0.0 | 0.0 | +0.0000 (+0.00pp) |
| Median RHAE | 0.0 | 0.0 | — |
| Levels completed | 0/7 (0.0%) | 0/7 (0.0%) | — |
| Full game wins | 0 | 0 | — |
| Total actions | 25 | 25 | — |
| Total tokens | 84,521 | 356,768 | — |
| RA²R API calls | 0 | 25 | — |
| Game wins (A vs B) | 0 | 0 | 1 ties |

## Per-Game Breakdown

| Game | Baseline RHAE | Augmented RHAE | Delta | Winner |
|------|--------------|----------------|-------|--------|
| LS20 | 0.0 | 0.0 | +0.0000 | tie |

## Methodology

- **Model**: Claude Opus 4.6 (both conditions)
- **Scoring**: RHAE (Relative Human Action Efficiency) — human_baseline_actions / agent_actions, capped at 1.0 per level
- **Condition A**: Game action tools only (baseline)
- **Condition B**: Game action tools + Ejentum RA²R Logic API as native tool (augmented)
- **RA²R usage**: Agent-initiated — the agent decides when to call the Logic API
- **Benchmark**: ARC-AGI-3 Interactive Reasoning Benchmark (arcprize.org)