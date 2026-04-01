# ARC-AGI-3 Research Summary & Benchmark Corrections

**Source:** Exploratory research session (Frank + Opus, Claude Chat, March 2026)
**Purpose:** Key findings that correct and refine the Ejentum ARC-AGI-3 benchmark harness

---

## Critical Corrections to Our Harness

### 1. SCORING FORMULA IS WRONG

**What we implemented:**
```
RHAE = min(1.0, human_actions / agent_actions)
```

**What ARC-AGI-3 actually uses:**
```
S(l,e) = min(1.0, (h(l,e) / a(l,e))^2)
```

The score is **SQUARED**. This changes everything:
- 2x human actions = 25% score (not 50%)
- 3x human actions = 11% score (not 33%)
- 10x human actions = 1% score (not 10%)

The squaring heavily punishes inefficiency. Our `scoring.py` must be updated.

### 2. PER-ENVIRONMENT SCORING IS LEVEL-WEIGHTED

**What we implemented:** Simple mean of level RHAEs

**What ARC-AGI-3 actually uses:** Triangular weighting -- later levels count more
```
E(e) = sum(l * S(l,e) for l in 1..n) / (n*(n+1)/2)
```
For a 6-level game: Level 1 = 1/21 weight, Level 6 = 6/21 weight.

This means early tutorial levels barely matter. Performance on harder levels dominates the score.

### 3. 5x ACTION CAP PER LEVEL

**What we implemented:** `MAX_ACTIONS_PER_LEVEL = 5` (for testing), designed for 25-150

**What ARC-AGI-3 actually uses:** Agent is cut off after 5x the human baseline per level.

For FT09 level 0 (human baseline = 17): cap = 85 actions, not a fixed number.
For FT09 level 4 (human baseline = 65): cap = 325 actions.

The cap should be dynamic per level: `5 * baseline_actions[level]`.

### 4. ONLY STATE-CHANGING INTERACTIONS COUNT

Internal computation, tool calls, reasoning chains do NOT count as actions. Only `env.step()` calls that change game state count. This means RA2R API calls are free -- they don't cost action budget. This is favorable for the augmented condition.

---

## Key Research Findings

### Game Selection Strategy

**Priority 1: FT09** (what we tested)
- Pattern matching across overlapping grids
- Reasoning domains: Abstraction, Analogical Reasoning
- Shortest reasoning chains, lowest token cost
- Best for initial signal detection

**Priority 2: LS20**
- Map navigation with symbol transformations
- Reasoning domains: Spatial, Causality, Abstraction
- Most documented game, strong community baseline data
- Level 1 random win probability: 1/355
- Has a three-life mechanic
- Actions: keyboard (directional movement)

**Priority 3: VC33** (optional)
- Volume adjustment to match target heights
- Reasoning domains: Simulation, Causality
- High token cost on later levels (level 6 requires 10x actions of level 1)

**Known results on other games:**
- TR87: Opus 4.6 scored 97.1% WITH harness, 0% without (massive harness effect)
- BP35: Opus 4.6 scored 0% with AND without harness

### Frontier Model Scores (Official Leaderboard at Launch)

| Model | Score |
|-------|-------|
| Gemini 3.1 Pro Preview | 0.37% |
| GPT 5.4 (High) | 0.26% |
| Opus 4.6 (Max) | 0.25% |
| Grok-4.20 | 0.00% |

All below 1%. The preview competition winner (StochasticGoose, 12.58%) used CNN + RL, not an LLM.

### Core Failure Modes of Frontier Models

1. **False hypothesis commitment** -- models imagine a game framework from initial visuals, then execute along wrong assumptions without self-correcting. They lack metacognitive ability.
2. **No state tracking** -- LLMs struggle with sustained sequential reasoning across hundreds of steps
3. **No learning from feedback** -- models don't update beliefs based on environmental response
4. **Knowledge-bound reasoning** -- reasoning is tied to training knowledge; ARC-AGI-3 environments are deliberately novel

### Logic API Opportunity Map

The ARC-AGI-3 technical report explicitly identifies these gaps:

| Gap | RA2R Domain |
|-----|-------------|
| Exploration (actively gathering info) | Simulation, Spatial |
| Modeling (building world models from observation) | Causality, Abstraction |
| Goal-Setting (identifying desirable states) | Metacognition |
| Planning & Execution (mapping paths + course-correcting) | Temporal, Simulation |

**Metacognition is the highest-leverage domain.** The #1 failure mode is models not recognizing their hypothesis is wrong. If RA2R metacognitive injections help the agent recognize "my current model might be wrong, I should explore differently," this alone could show measurable improvement.

**Multi-ability retrieval is key for harder levels.** Later levels introduce composed mechanics. Single-domain reasoning won't suffice. The augmented condition should use `mode: "multi"` on levels 3+.

---

## Updated Environment Details

### Full Specification (from technical report)

- **135 total environments** (25 public, 55 semi-private, 55 fully private)
- **1,000+ levels** across 150+ handcrafted environments
- **Each game: ~8-10 levels** with progressively introduced mechanics
- **Grid: 64x64**, each cell is one of 16 possible colors
- **Turn-based** (not real-time) -- prioritizes offline reasoning
- **Level 1 is always tutorial** (intentionally easy)
- **Multiple mechanics per environment** (single-mechanic scaling is an anti-pattern)

### Core Knowledge Priors Only
Games use ONLY these concepts:
- Objectness: coherent, persistent entities
- Basic geometry/topology: symmetries, rotations, inside/outside
- Basic physics: gravity, momentum, bouncing
- Agentness: recognizing objects with intent
- NO language, numbers, letters, cultural symbols

### Validation Thresholds
- Random policy must not solve a level more than 1 in 10,000 times
- Each environment tested with 10 humans; must be solved by at least 2
- Human baseline = second-best human (removes outlier)

---

## Official System Prompt

The official system prompt used for all ARC-AGI-3 evaluations:

```
You are playing a game. Your goal is to win. Reply with the exact action
you want to take. The final action in your reply will be executed next turn.
Your entire reply will be carried to the next turn.
```

Note: Our system prompts are much longer. This is intentional -- we need JSON output, game state parsing, and scaffold absorption instructions. But we should test with the official prompt as a control condition.

---

## Competition Context

- **ARC Prize 2026:** $2M total prize pool
- **ARC-AGI-3 Track:** $850K ($700K grand prize for 100% score)
- **Milestone 1:** June 30, 2026
- **Milestone 2:** September 30, 2026
- **Rules:** Winning solutions must be open-sourced, no external APIs on official leaderboard
- **Community leaderboard:** Allows self-reported harness-driven results (our path)

---

## What This Means for Our Benchmark

### Immediate Fixes Needed

1. **Fix scoring formula** in `scoring.py`: square the ratio
2. **Add level-weighted scoring**: triangular weights for per-game score
3. **Dynamic action cap**: `5 * baseline_actions[level]` instead of fixed cap
4. **Test on LS20 next**: different input modality (keyboard vs click), richer mechanics
5. **Use `multi` mode on levels 3+**: composed mechanics need multi-ability retrieval

### Strategic Implications

- **Metacognition is our strongest play.** The #1 failure mode (false hypothesis commitment) is exactly what RA2R metacognitive suppression addresses. "Suppress: premature_conclusion, forward_momentum_bias" directly targets this.
- **RA2R calls are free actions.** They don't count against the action budget. The augmented condition has no action-cost disadvantage.
- **TR87 shows harness effect is massive.** 97.1% with harness vs 0% without. Even basic scaffolding makes an enormous difference. RA2R is more than basic scaffolding.
- **Community leaderboard is our target.** We can't submit to the official leaderboard (no external APIs), but the community leaderboard accepts harness-driven results with self-reported scores.

### Revised Hypothesis

The original hypothesis was generic: "RA2R will improve RHAE." The research sharpens it:

**RA2R metacognitive injections will reduce false hypothesis commitment -- the #1 failure mode of frontier models on ARC-AGI-3 -- by triggering explicit self-correction when the agent's game model fails to predict observed state changes. This effect will be strongest on levels 2-5 where initial tutorial hypotheses must be revised as new mechanics are introduced.**

---

## Sources

- ARC-AGI-3 Technical Report: https://arcprize.org/media/ARC_AGI_3_Technical_Report.pdf
- Docs: https://docs.arcprize.org/
- Toolkit: https://github.com/arcprize/ARC-AGI
- Play games: https://three.arcprize.org/games/ls20
- ARC Prize 2026: https://arcprize.org/competitions/2026/arc-agi-3