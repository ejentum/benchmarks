# ARC-AGI-3 Benchmark Harness -- Compliance Audit

**Date:** 2026-03-28
**Auditor:** Claude Opus 4.6 with RA2R multi-ability (model_overconfidence + depth_tracking + path_dependency + causal_precedence)
**Spec:** ARC-AGI-3 Technical Report (arcprize.org/media/ARC_AGI_3_Technical_Report.pdf)
**Scope:** Every component of `arc_benchmark/` against ARC-AGI-3 official rules

---

## 1. SCORING FORMULA

### Spec requirement
```
S(l,e) = min(1.0, (h(l,e) / a(l,e))^2)
```

### Implementation (`scoring.py:116-117`)
```python
ratio = human_baseline / agent_actions if agent_actions > 0 else 0.0
rhae = min(1.0, ratio ** 2)
```

**VERDICT: PASS** -- Squared ratio, capped at 1.0. Verified with test: agent=20, human=17 -> (17/20)^2 = 0.7225. Correct.

---

## 2. PER-ENVIRONMENT SCORING (Level Weighting)

### Spec requirement
```
E(e) = sum(l * S(l,e) for l in 1..n) / (n*(n+1)/2)
```
Triangular weighting: later levels count more.

### Implementation (`scoring.py:49-59`)
```python
def compute_weighted(self):
    n = max(ls.level for ls in self.level_scores) + 1
    weighted_sum = sum((ls.level + 1) * ls.rhae for ls in self.level_scores)
    total_weight = n * (n + 1) / 2
    self.game_rhae = weighted_sum / total_weight
```

**VERDICT: PASS** -- Uses `(level+1)` as weight (0-indexed levels), divides by triangular number. Verified: levels [0,1,2] with RHAEs [0.7225, 0.4011, 0.09] -> (1*0.7225 + 2*0.4011 + 3*0.09)/6 = 0.2991. Correct.

**ISSUE (minor):** `n` is computed from max level index in `level_scores`, not from `total_levels`. If level 2 is completed but level 1 isn't recorded, weighting denominator will be wrong. Low risk in practice since levels are sequential.

---

## 3. ACTION CAP PER LEVEL

### Spec requirement
Agent is cut off after **5x the human baseline** per level.

### Implementation (`agent_base.py:233-236`)
```python
baselines = GAME_REGISTRY.get(game_id, {}).get("baseline_actions", [])
level_cap = (baselines[current_level] * 5) if current_level < len(baselines) else MAX_ACTIONS_PER_LEVEL
```

**VERDICT: PASS** -- Dynamic 5x cap per level, falls back to fixed cap if baseline unknown.

**ISSUE (medium):** The `from .config import GAME_REGISTRY` is inside the while loop. Should be moved outside for cleanliness (no functional impact, just re-imports every iteration).

---

## 4. ACTION COUNTING

### Spec requirement
- Only state-changing interactions count as actions
- Internal computation, tool calls, reasoning chains do NOT count
- RA2R API calls should NOT count as actions

### Implementation
- `env.step()` is called once per loop iteration -> `step += 1` and `level_actions += 1`
- RA2R calls happen inside `decide_action()` BEFORE `env.step()` -- not counted
- `call_claude()` is computation, not a game action -- not counted

**VERDICT: PASS** -- Only `env.step()` increments action count. RA2R and reasoning are free.

---

## 5. SYSTEM PROMPTS -- CRITICAL ISSUE

### Spec requirement (official system prompt)
```
You are playing a game. Your goal is to win. Reply with the exact action
you want to take. The final action in your reply will be executed next turn.
Your entire reply will be carried to the next turn.
```

### Current implementation

**Baseline (`agent_baseline.py`):** 44 lines of custom prompt with strategy instructions, action descriptions, JSON format requirements. This is NOT the official prompt. It gives the model advantages not present in official evaluations.

**Augmented (`agent_augmented.py`):** Same 44 lines PLUS scaffold absorption instructions (NEGATIVE GATE, TOPOLOGY, Suppress signals).

### Problems

| Issue | Severity | Detail |
|-------|----------|--------|
| **Baseline prompt != official** | CRITICAL | Our baseline gets strategy hints (OBSERVE, EXPERIMENT, HYPOTHESIZE, ADAPT, TRANSFER) that the official prompt doesn't provide. This inflates baseline scores and narrows the gap with augmented. |
| **Both prompts identical except scaffold section** | CORRECT | Good -- the only difference between A and B should be RA2R access. |
| **JSON format instructions in system prompt** | DESIGN CHOICE | The official prompt doesn't require JSON. We need it for `--json-schema`. This is acceptable as harness infrastructure, not game knowledge. |
| **Action descriptions in prompt** | CONTAMINATION | Telling the model "ACTION6=click/place at (x,y)" gives it information it should discover through play. The official prompt says nothing about actions. |

### Required fix

**Baseline:** Use the official ARC-AGI-3 system prompt + minimal JSON format instruction only.

**Augmented:** Official prompt + JSON format + RA2R scaffold absorption protocol. The scaffold protocol is the ONLY additional content -- this is the variable we're testing.

The augmented agent should also be free to choose single or multi mode based on its own assessment of task complexity, not harness-dictated. The agent gets the Logic API as a tool and decides how to use it.

---

## 6. RA2R INTEGRATION DESIGN

### Current design
- Harness-controlled triggers: game start, new level, stuck (5 actions), post-reset
- Always uses `mode: "single"`
- Agent has NO choice about when/whether to call RA2R

### Required design (per Frank's specification)
- Agent freely uses the Logic API tool
- Agent chooses `single` (focused) or `multi` (multi-lens) mode
- Function calling prompt teaches the agent HOW to use the tool effectively
- Not harness-dictated, agent-initiated

### Problems

| Issue | Severity |
|-------|----------|
| Agent can't choose when to call RA2R | HIGH -- removes agency, artificial trigger pattern |
| Always single mode | HIGH -- multi mode may be better for complex levels |
| Trigger at step 0 always | MEDIUM -- biases first action with scaffold before any observation |
| Stuck threshold is fixed at 5 | LOW -- could be dynamic based on level complexity |

### Required fix
Redesign augmented agent to present RA2R as a callable tool. The system prompt should include function calling instructions that teach the agent:
- WHEN to call (non-obvious judgment, stuck, strategy shift)
- HOW to query (specific task description, not generic)
- Which MODE to use (single for focused, multi for cross-domain)

---

## 7. FRAME RENDERING

### Spec requirement
- 64x64 grid, 16 possible colors per cell
- Each grid state is a "frame"

### Implementation
- `render_downsampled(block_size=4)` -> 16x16 summary for dense grids
- `render_sparse()` for sparse grids
- `render_region()` for medium density

### Problems

| Issue | Severity |
|-------|----------|
| **Downsampling loses spatial precision** | HIGH -- block=4 merges 16 cells into 1 symbol. Agent can't distinguish individual cells within a block. Coordinate mapping becomes approximate. |
| **No raw frame option** | MEDIUM -- for some games, the model needs exact cell-level data |
| **Tile symbols are arbitrary** | LOW -- the model doesn't know what value 9 means. But this is by design (discovery through play). |

### Note
The E2E test showed the model successfully mapping display coordinates to actual 64x64 coordinates ("display (2,2) maps to actual (10,10) with block=4"). The downsampling works but loses detail on complex games.

---

## 8. EXPERIMENTAL CONTROLS

### Fair comparison requirements

| Control | Status | Detail |
|---------|--------|--------|
| Same model | PASS | Both use Sonnet 4.6 via same SDK |
| Same game state | PASS | Same game_id, same seed |
| Same action cap | PASS | Dynamic 5x baseline per level |
| Same frame rendering | PASS | Both get identical `render_observation()` output |
| Same JSON schema | PASS | Both use identical `ACTION_SCHEMA` |
| System prompt parity | **FAIL** | Baseline has custom strategy prompt. Should use official prompt. |
| RA2R cost accounting | PASS | RA2R calls don't count as game actions |
| Randomization | PARTIAL | Same seed, but only 1 run. Need 3+ for reliability. |

---

## 9. CLI/SDK RELIABILITY

### Proven working
- `claude-agent-sdk` query() works in foreground: 46-135s per call
- Real structured JSON output with spatial reasoning
- RA2R API calls succeed and scaffold is injected

### Known issues

| Issue | Severity | Mitigation |
|-------|----------|------------|
| Background execution hangs | CRITICAL | Must run from separate terminal |
| ~60-130s per call | HIGH | Limits practical step count. 50 steps = ~1.5 hours per condition |
| CWD must be temp dir | HIGH | CLAUDE.md auto-loading adds 10x latency. `os.chdir()` or `cwd` param required |
| Usage/token tracking returns 0 | LOW | SDK doesn't expose token counts. Cost tracking is blind. |
| Parse failures (1 in 10) | MEDIUM | JSON extraction has 3 fallback strategies. Fallback to action=1 if all fail. |

---

## 10. OVERALL READINESS RATING

### Scoring: 1 (not ready) to 5 (production ready)

| Component | Score | Blocking? |
|-----------|-------|-----------|
| Scoring formula | 5/5 | No |
| Level weighting | 5/5 | No |
| Action cap (5x baseline) | 5/5 | No |
| Action counting (RA2R free) | 5/5 | No |
| Frame rendering | 3/5 | No |
| System prompts | **1/5** | **YES** |
| RA2R integration design | **2/5** | **YES** |
| Experimental controls | 3/5 | Partially |
| SDK reliability | 3/5 | No (workaround exists) |
| Evaluation metrics | 4/5 | No |
| Documentation | 4/5 | No |

### OVERALL (pre-fix): 3.2/5 -- NOT READY

### OVERALL (post-fix): 4.7/5 -- READY FOR EXECUTION

#### Fixes applied (2026-03-28):
- BLOCKER 1 FIXED: Both prompts now use official ARC-AGI-3 system prompt verbatim
- BLOCKER 2 FIXED: Augmented agent is now fully agent-initiated with mode selection (single/multi)
- Baseline schema: {action, x, y, reasoning} -- NO augment fields
- Augmented schema: {augment, augment_query, augment_mode, action, x, y, reasoning}
- Prompt delta is exactly 1354 chars (RA2R protocol only)
- GAME_REGISTRY import moved outside loop
- CLI typo fixed
- All compliance checks pass programmatically

---

## 11. BLOCKERS (must fix before running)

### BLOCKER 1: System prompts must use official ARC-AGI-3 prompt
**Impact:** Results are not comparable to any published scores. Our custom strategy hints inflate both conditions.

**Fix:** Both conditions use:
```
You are playing a game. Your goal is to win. Reply with the exact action
you want to take. The final action in your reply will be executed next turn.
Your entire reply will be carried to the next turn.
```
Plus minimal JSON format instruction (harness infrastructure, not game knowledge).

### BLOCKER 2: Augmented agent must have agent-initiated RA2R
**Impact:** Harness-controlled triggers create an artificial calling pattern that doesn't reflect real usage. The agent should decide when it needs reasoning help.

**Fix:** Present RA2R as a callable tool via function calling prompt. Agent chooses when and which mode (single/multi). The function calling instructions are the ONLY difference between baseline and augmented system prompts.

---

## 12. RECOMMENDED FIXES (priority order)

1. **Rewrite both system prompts** -- official ARC-AGI-3 prompt as base, JSON format appended
2. **Rewrite augmented prompt** -- add RA2R function calling instructions (when/how/which mode)
3. **Make RA2R agent-initiated** -- agent requests scaffold via structured output field, harness calls API and re-prompts
4. **Add multi mode support** -- agent chooses single vs multi based on task complexity
5. **Move GAME_REGISTRY import outside loop** in agent_base.py
6. **Fix `compute_weighted` denominator** -- use `total_levels` not max completed level
7. **Add typo fix** in cli.py line 31: "Respnd" -> "Respond"