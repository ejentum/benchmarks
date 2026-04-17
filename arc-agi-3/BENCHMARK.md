# ARC-AGI-3 Benchmark — Ejentum RA²R Logic API

## What This Is

An A/B benchmark comparing **raw Claude Opus 4.6** against **Claude Opus 4.6 with native RA²R Logic API tool calling** on the ARC-AGI-3 Interactive Reasoning Benchmark.

**ARC-AGI-3** is the world's only unbeaten AI benchmark. It measures an agent's ability to explore, learn, and adapt in novel interactive game environments — without instructions, rules, or stated objectives. Current frontier AI performance: **0.26%**. Human performance: **100%**.

This benchmark tests whether RA²R cognitive injection improves an LLM's interactive reasoning capabilities — exploration strategy, pattern recognition, causal inference, spatial reasoning, and metacognitive adaptation — in a completely unsaturated, externally validated evaluation framework.

---

## Why ARC-AGI-3

| Property | Why it matters for RA²R |
|----------|----------------------|
| **Unbeaten** | 0.26% frontier score. Any measurable improvement is newsworthy |
| **Interactive** | Multi-step reasoning under uncertainty — exactly where attention decay compounds |
| **No memorization** | Tasks can't be solved from training data. Tests genuine reasoning |
| **Action efficiency** | RHAE scoring measures reasoning quality per decision, not just correctness |
| **External credibility** | Created by François Chollet. $2M prize. All major labs benchmark on it |
| **Unsaturated** | Massive headroom — small improvements are visible above noise |

---

## Architecture

```
┌──────────────────────────────────────────┐
│           CONDITION A (Baseline)          │
│                                           │
│   Claude Opus 4.6                         │
│   ├─ System prompt: exploration strategy  │
│   ├─ Tool: take_action (game actions 0-7) │
│   └─ No RA²R access                      │
└───────────────┬───────────────────────────┘
                │  Same games, same seeds
┌───────────────┴───────────────────────────┐
│           CONDITION B (Augmented)          │
│                                           │
│   Claude Opus 4.6                         │
│   ├─ System prompt: exploration strategy  │
│   ├─ Tool 1: take_action (game actions)   │
│   └─ Tool 2: query_logic_api (RA²R)      │
│        ↳ Agent-initiated                  │
│        ↳ Returns cognitive injection       │
│        ↳ Agent absorbs before deciding    │
└───────────────────────────────────────────┘
```

**Critical design**: In Condition B, the agent **chooses when** to call RA²R — it's not force-injected. This mirrors real production usage and tests whether the agent recognizes when its own reasoning needs augmentation.

---

## How ARC-AGI-3 Games Work

Each game is a **video-game-like interactive environment**:
- **64x64 tile grid** — each cell is an int8 value representing a tile/object type
- **7 action types**: ACTION1-5 (movement/abilities), ACTION6 (x,y coordinate click), ACTION7 (undo), RESET
- **Multiple levels** per game, increasing in difficulty
- **No instructions** — agent must discover rules through trial and error
- **Human baseline** — 2nd-best human action count per level (for RHAE scoring)

The agent receives the grid as a text-rendered observation (sparse tiles, region-of-interest crops, or downsampled overviews depending on density) and selects actions through Claude tool calling.

---

## Scoring: RHAE (Relative Human Action Efficiency)

The official ARC-AGI-3 scoring metric:

```
Per level:   RHAE = min(1.0, human_baseline_actions / agent_actions)
Per game:    RHAE = mean(level RHAEs)
Overall:     RHAE = mean(game RHAEs)   →   0% to 100%
```

- **100%**: Agent matches or beats human efficiency on every level
- **0%**: Agent completes no levels
- Capped at 1.0 per level to prevent gaming through exploits
- Uncompleted levels score 0

---

## Game Registry

25 public games available, 10 selected for default benchmark:

| Game | Tags | Levels | Human Baseline (actions per level) |
|------|------|--------|-----------------------------------|
| R11L | click | 6 | [7, 28, 30, 20, 37, 45] |
| TN36 | click | 7 | [23, 22, 26, 37, 25, 56, 61] |
| VC33 | click | 7 | [6, 13, 31, 59, 92, 24, 82] |
| TR87 | keyboard | 6 | [37, 30, 39, 29, 63, 119] |
| FT09 | — | 6 | [17, 19, 15, 21, 65, 26] |
| CD82 | keyboard_click | 6 | [41, 8, 30, 21, 19, 17] |
| SB26 | keyboard_click | 8 | [18, 16, 15, 15, 31, 24, 17, 17] |
| TU93 | keyboard_click | 9 | [19, 15, 34, 42, 76, 91, 47, 23, 31] |
| SC25 | keyboard_click | 6 | [39, 5, 32, 33, 66, 41] |
| SP80 | keyboard_click | 6 | [11, 18, 17, 172, 102, 152] |

Selection criteria: mix of input modalities (click, keyboard, both), varying difficulty, manageable level counts.

---

## File Structure

```
arc_benchmark/
├── __init__.py           # Package marker
├── __main__.py           # python -m arc_benchmark entry
├── config.py             # API keys, constants, game registry
├── frame_renderer.py     # 64x64 numpy grid → text for Claude
│   ├── render_sparse()       Sparse: list non-background tile coordinates
│   ├── render_region()       ROI: crop to bounding box, render grid
│   ├── render_downsampled()  Overview: 8x8 block summary
│   └── render_frame()        Auto-select strategy by density
├── agent_base.py         # Abstract base: game loop, logging, action records
│   ├── BaseAgent              ABC with decide_action()
│   ├── ActionRecord           Per-action data (step, level, reasoning, tokens)
│   └── GameResult             Per-game data (levels, actions, scores, errors)
├── agent_baseline.py     # Condition A: Claude via CLI, game actions only
│   └── BaselineAgent          Structured JSON output, no augmentation
├── agent_augmented.py    # Condition B: Claude via CLI + RA²R
│   └── AugmentedAgent         Two-pass: augment request → injection → action
│                              Agent decides when to call RA²R
├── scoring.py            # RHAE calculation and A/B comparison
│   ├── score_game_result()    Per-game RHAE from result JSON
│   ├── compare_conditions()   Full A vs B statistical comparison
│   └── format_comparison_report()  Markdown report generation
├── harness.py            # Orchestrator
│   └── BenchmarkHarness       Runs both conditions, generates reports
├── run.py                # CLI entry point with argparse
├── BENCHMARK.md          # This document
├── results/              # Auto-created per benchmark run
│   └── benchmark_YYYYMMDD_HHMMSS/
│       ├── config.json           Run parameters
│       ├── A_baseline__*.json    Per-game result files
│       ├── B_augmented__*.json   Per-game result files
│       ├── comparison.json       Scored comparison data
│       └── REPORT.md             Human-readable report
└── logs/                 # Structured logs per run
    └── benchmark_*.log
```

---

## Usage

### Prerequisites

```bash
pip install arc-agi python-dotenv httpx
```

**No Anthropic API key needed** — agents use the `claude` CLI (Claude Code), which is already authenticated.

Required in `.env` (project root):
```
ARC_API_KEY=your-arc-agi-3-api-key
EJENTUM_API_KEY=YOUR_EJENTUM_API_KEY
EJENTUM_API_URL=https://ejentum-main-ab125c3.zuplo.app/logicv1/
```

### Run Benchmark

```bash
# Smoke test: 1 game, 1 run, both conditions
python -m arc_benchmark --smoke

# Full benchmark: 10 games, 3 runs each, both conditions
python -m arc_benchmark

# Single condition
python -m arc_benchmark --condition A_baseline
python -m arc_benchmark --condition B_augmented

# Custom game set, fewer runs
python -m arc_benchmark --games ft09-0d8bbf25 r11l-aa269680 --runs 1

# Score existing results
python -m arc_benchmark --score-only arc_benchmark/results/benchmark_20260327_180000

# List all available games
python -m arc_benchmark --list-games
```

---

## What Gets Measured

### Tier 1: RHAE (Official ARC-AGI-3 Metric)

| Metric | Source | Purpose |
|--------|--------|---------|
| **RHAE per level** | scoring.py | Action efficiency vs human baseline |
| **RHAE per game** | scoring.py | Mean level efficiency |
| **Mean RHAE delta** | scoring.py | Primary outcome: B - A |
| **Levels completed** | agent_base.py | Raw capability |
| **Total actions** | agent_base.py | Efficiency |
| **Tokens consumed** | both agents | Cost comparison |

### Tier 2: Interactive Reasoning Metrics (ARC-AGI-3 Native)

Computed from action logs — no LLM judge. These measure capabilities unique to interactive benchmarks.

| Metric | Source | What it reveals |
|--------|--------|-----------------|
| **Exploration waste ratio** | evaluation.py | Actions on never-completed levels / total. Lower = efficient exploration |
| **Actions before first progress** | evaluation.py | Steps until first level clear. Lower = faster goal inference |
| **Learning slope** | evaluation.py | Trend of per-level RHAE across levels. Positive = transfer learning |
| **Adaptation rate** | evaluation.py | 1/avg repeated failed actions before switching. Higher = faster adaptation |
| **Stuck episodes** | evaluation.py | Count of 3+ consecutive identical actions. Lower = better metacognition |
| **Entropy convergence** | evaluation.py | Early action entropy - late. Positive = explore→exploit pattern |
| **Recovery speed** | evaluation.py | Actions to regain progress after reset. Lower = better memory |
| **Goal discovery ratio** | evaluation.py | First-progress step / total. Lower = faster goal discovery |

### Tier 3: RA²R Self-Awareness (Condition B Only)

| Metric | Source | What it reveals |
|--------|--------|-----------------|
| **RA²R call count** | evaluation.py | Total reasoning augmentation requests |
| **Breakthrough rate** | evaluation.py | Calls within 10 steps of level clear / total calls. Higher = right-moment calling |
| **Stuck-call correlation** | evaluation.py | Calls during stuck episodes / total. Higher = recognizes reasoning limits |

---

## Methodological Controls

| Control | Implementation |
|---------|----------------|
| **Same model** | Claude Opus 4.6 for both conditions |
| **Same system prompt** | Identical game instructions (B adds RA²R usage guidance) |
| **Same games, same seeds** | Deterministic game state |
| **Same action cap** | 500 actions/game, 150 actions/level |
| **Agent-initiated RA²R** | Not force-injected — agent decides when to call |
| **Blind scoring** | RHAE computed from action counts, not subjective evaluation |
| **Multiple runs** | 3 runs per game per condition (configurable) |
| **Conversation windowing** | Last 20 turns to prevent context overflow |

---

## Hypothesis

RA²R cognitive injection will improve interactive reasoning performance because ARC-AGI-3 games require exactly the capabilities RA²R enhances:

| ARC-AGI-3 Requirement | RA²R Domain |
|------------------------|-------------|
| Explore unknown environments | Metacognitive — curiosity-driven exploration |
| Learn rules from observation | Causal — root cause from observation sequences |
| Remember across levels | Temporal — pattern persistence |
| Adapt when stuck | Metacognitive — M-nodes, strategy switching |
| Efficient action selection | Abstract — invariant patterns, strategy compression |
| Spatial pattern recognition | Spatial — topology validation, containment |

Prediction: Condition B will show higher RHAE, complete more levels, and RA²R calls will concentrate at exploration boundaries (new games, new levels, strategy failures).

---

## Relationship to Existing Ejentum Benchmarks

| Benchmark | Domain | Tasks | Key Metric |
|-----------|--------|-------|------------|
| BBH/CausalBench/MuSR | Academic reasoning | 70 published | Correctness (+7.1pp) |
| EjBench | Professional domains | 180 custom | 7-factor composite |
| Beyond-Reasoning | Behavioral signals | 140 tasks | Structure (+22.5%) |
| **ARC-AGI-3** | **Interactive reasoning** | **25 games, 175 levels** | **RHAE (action efficiency)** |

ARC-AGI-3 fills the gap: no existing Ejentum benchmark tests sustained multi-step interactive reasoning. All current benchmarks are single-turn or short-chain. ARC-AGI-3 tests exactly the scenario where RA²R's Cognitive Scaffolding Thesis predicts the largest effect — long execution chains with compounding attention decay.

### What Makes These Metrics New

Existing Ejentum benchmarks (BBH, EjBench, Beyond-Reasoning) measure reasoning quality on static tasks. ARC-AGI-3 interactive metrics measure **reasoning dynamics** — how reasoning quality changes over time within a single session:

- **Learning slope** captures whether RA²R helps agents transfer knowledge across levels — impossible to measure in single-turn benchmarks
- **Adaptation rate** measures metacognitive self-correction in real time — not retrospective
- **Entropy convergence** reveals explore→exploit transitions — a signature of intelligent search
- **RA²R breakthrough rate** tests whether the agent calls for help at the right moment — a form of self-awareness our existing benchmarks can't isolate
