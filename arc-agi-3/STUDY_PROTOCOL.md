# Ejentum RA2R Logic API -- ARC-AGI-3 Flagship Study Protocol

## Thesis

RA2R cognitive injection augments LLM interactive reasoning capabilities toward AGI-level performance by preventing the #1 frontier model failure mode on ARC-AGI-3: false hypothesis commitment. The Logic API's metacognitive suppression signals enable the agent to recognize when its game model is wrong, triggering self-correction that raw models cannot achieve.

## Study Design

**Benchmark:** ARC-AGI-3 Interactive Reasoning Benchmark (arcprize.org)
**Game:** LS20 -- map navigation with symbol transformations
**Model:** Claude Sonnet 4.6 (both conditions)
**Method:** A/B comparison, same game, same seed, same frame rendering

### Why LS20

| Requirement | LS20 Mechanic | RA2R Domain |
|-------------|---------------|-------------|
| Spatial navigation | Map corridors, walls, markers | Spatial |
| Causal inference | Symbol transformation rules | Causal |
| Hypothesis revision | 3-life mechanic forces strategy correction | Metacognition |
| Multi-step planning | 7 levels with progressive difficulty | Temporal, Simulation |
| Transfer learning | Mechanics compose across levels | Abstraction |

LS20 is the most documented ARC-AGI-3 game with community baselines. Random win probability on level 1 is 1/355 -- this is not solvable by chance.

### Conditions

**Condition A (Baseline):**
- Official ARC-AGI-3 system prompt (verbatim)
- JSON format instruction (harness infrastructure)
- NO strategy hints, NO action descriptions, NO RA2R access

**Condition B (Augmented):**
- Same official prompt + JSON instruction (identical to A)
- RA2R function calling protocol (the ONLY addition)
- Agent freely decides when to call RA2R
- Agent chooses mode: reasoning (focused) or reasoning-multi (cross-domain)
- Agent writes its own query describing its reasoning challenge

### Parameters

| Parameter | Value | Justification |
|-----------|-------|---------------|
| Game | LS20 (ls20-9607627b) | Best RA2R domain alignment |
| Levels | 7 | Full game |
| Per-level cap | 5x human baseline | ARC-AGI-3 official rule |
| Level caps | [105, 615, 195, 460, 270, 540, 545] | 5x * [21, 123, 39, 92, 54, 108, 109] |
| Global cap | 500 | Cost control (~$25-50 per condition) |
| Runs per condition | 1 (initial), 3 (full study) | Statistical reliability |
| Seed | 0 | Deterministic game state |
| Model | Sonnet 4.6 | Via claude-agent-sdk, same auth |
| Frame rendering | Downsampled 16x16 (block=4) | ~515 chars per frame |
| Actions available | [1, 2, 3, 4] | Keyboard directional (no coordinate clicks) |

### Scoring (ARC-AGI-3 Official)

```
Per level:  S(l,e) = min(1.0, (human_baseline / agent_actions)^2)
Per game:   E(e) = sum((l+1) * S(l,e)) / (n*(n+1)/2)   [triangular weighting]
```

Only state-changing actions count. RA2R API calls are free (not counted as actions).

## Measurement Framework

### Tier 1: RHAE (Primary Outcome)
- Per-level RHAE (squared ratio vs human baseline)
- Weighted game RHAE (later levels count more)
- Levels completed (A vs B)

### Tier 2: Interactive Reasoning Metrics (Signal Even at 0% RHAE)
- Exploration waste ratio
- Goal discovery ratio (speed to first level clear)
- Adaptation rate (strategy switching when stuck)
- Entropy convergence (explore-then-exploit pattern)
- Learning slope (transfer across levels)
- Recovery speed (actions after reset to regain progress)

### Tier 3: RA2R Self-Awareness (Condition B Only)
- Total RA2R calls
- Mode distribution (single vs multi)
- Query quality (what the agent asks for)
- Breakthrough rate (calls within 10 steps of level clear)
- Stuck-call correlation (calls during stuck episodes)

### Tier 4: Qualitative + Cost
- Reasoning quality comparison (spatial analysis depth, hypothesis revision, suppress compliance)
- JSON compliance rate
- Cost per action (tokens, dollars)
- Response latency (API ms, wall time)

## Data Captured Per Action

| Field | Type | Description |
|-------|------|-------------|
| step | int | Action number (1-indexed) |
| level | int | Current level |
| action | string | ACTION1-4 name |
| coords | dict/null | x,y for ACTION6 (not used in LS20) |
| reasoning | string | Agent's reasoning (1000 char max) |
| state_after | string | Game state after action |
| levels_completed_after | int | Levels cleared so far |
| rar_called | bool | Whether RA2R was called this turn |
| rar_query | string | What the agent asked RA2R (B only) |
| rar_mode | string | reasoning or reasoning-multi (B only) |
| cost_usd | float | Dollar cost of this turn |
| duration_api_ms | int | API response time |
| tokens_used | int | Input + output tokens |

## Execution

### Prerequisites
```
pip install arc-agi claude-agent-sdk python-dotenv httpx
```

### Run
```
Open a NEW terminal (not Claude Code). Then:

cd %TEMP%
set PYTHONPATH=c:\Users\frank\Desktop\ejentum
python -m arc_benchmark --smoke
```

Or double-click `RUN_BENCHMARK.bat`.

### Expected Duration
- ~60-90 seconds per action (Sonnet 4.6 via SDK)
- 500 max actions per condition
- Estimated: 2-4 hours per condition, 4-8 hours total
- If agent clears levels efficiently: could be faster

### Expected Cost
- ~$0.01-0.05 per action (Sonnet 4.6)
- 500 actions per condition = $5-25 per condition
- Total: $10-50 for both conditions

## Success Criteria

### Minimum Viable Result
The study produces meaningful data if ANY of these are true:
1. One condition completes more levels than the other
2. Exploration waste ratio differs by >10%
3. Augmented agent's reasoning shows systematic injection absorption
4. RA2R calls correlate with subsequent progress

### Ideal Result
1. Augmented condition has higher RHAE
2. Augmented completes more levels
3. RA2R calls show >50% breakthrough rate
4. Qualitative reasoning shows metacognitive self-correction absent in baseline

### What Would Falsify Our Thesis
1. Both conditions perform identically on all metrics
2. RA2R calls show 0% breakthrough rate AND no qualitative reasoning improvement
3. Augmented performs WORSE (injection confuses the agent)

## Output Files

```
arc_benchmark/results/<timestamp>/
  A_baseline__ls20-9607627b__0.json      Full action log
  B_augmented__ls20-9607627b__0.json     Full action log + RA2R data
  comparison.json                         Scored A vs B
  interactive_metrics.json                8 interactive metrics
  REPORT.md                               Human-readable report
  INTERACTIVE_REPORT.md                   Interactive metrics report
```
