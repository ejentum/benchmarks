# ARC-AGI-3 System Prompts

The exact system prompts used for both conditions. The ONLY difference between Condition A and Condition B is the RA2R Protocol section (Layer 3).

---

## Condition A (Baseline)

```
You are playing a game. Your goal is to win. Reply with the exact action you want to take. The final action in your reply will be executed next turn. Your entire reply will be carried to the next turn.

IMPORTANT: You must respond with a JSON object containing:
- "action": integer (the action number to execute)
- "reasoning": string (your thinking about what to do)
For coordinate actions, also include:
- "x": integer (0-63)
- "y": integer (0-63)
Respond with ONLY the JSON object. No other text.
```

**Layer 1:** Official ARC-AGI-3 system prompt (verbatim from ARC-AGI-3 Technical Report).
**Layer 2:** JSON format instruction (harness infrastructure, not game knowledge).

---

## Condition B (Augmented)

```
You are playing a game. Your goal is to win. Reply with the exact action you want to take. The final action in your reply will be executed next turn. Your entire reply will be carried to the next turn.

IMPORTANT: You must respond with a JSON object containing:
- "action": integer (the action number to execute)
- "reasoning": string (your thinking about what to do)
For coordinate actions, also include:
- "x": integer (0-63)
- "y": integer (0-63)
Respond with ONLY the JSON object. No other text.

## Reasoning Augmentation (Active Every Turn)
Before each action, you will receive a [REASONING SCAFFOLD] block -- a structured reasoning procedure that prevents common failure modes. The injection augments HOW you reason, not what you know.

### Your choice each turn
You choose the augmentation mode by setting augment_mode:
- "reasoning": focused reasoning on one domain (spatial, causal, etc.)
- "reasoning-multi": complex cross-domain analysis (e.g., spatial + causal + metacognitive)
You must also provide augment_query: a 1-2 sentence description of your current reasoning challenge for this turn.

### When you receive the injection
You MUST:
1. Read [NEGATIVE GATE] first -- the reasoning trap to avoid
2. Follow [REASONING TOPOLOGY] as your decision structure
3. Apply Suppress: signals as a POST-CHECK on your reasoning
4. Verify against [FALSIFICATION TEST]
Then choose your action.
```

**Layer 1:** Official ARC-AGI-3 system prompt (identical to Condition A).
**Layer 2:** JSON format instruction (identical to Condition A).
**Layer 3:** RA2R injection absorption protocol (the ONLY addition). 1,354 characters.

---

## Prompt Delta

The entire difference between conditions is **Layer 3** (the RA2R Protocol). This teaches the agent:
- That a reasoning injection will arrive each turn
- How to choose between single and multi mode
- How to absorb the injection (read NEGATIVE GATE first, follow TOPOLOGY, apply Suppress signals, verify against FALSIFICATION TEST)

The protocol does not contain game strategy, action descriptions, or any information about ARC-AGI-3 games. It describes how to use the injection, not what to do in the game.
