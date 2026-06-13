# Results

Regenerate any number with `python run.py tasks/<task> results/<task>_<model>`,
or `python tasks/<task>/oracle.py` for trap validity. The oracle is the source of
truth; there is no LLM in the scoring path.

## The traps are live (auditability is exercised against a real fork)

| task | vectors | wrong frame | fails |
|---|---|---|---|
| word_wrap | 55 (30 disc / 18 basic / 7 edge) | greedy line-filling | 30/30 discriminating |
| apply_ops | 25 (10 cascade / 4 priority / 6 basic / 5 edge) | sequential `str.replace` | 10/10 cascade |
| apply_ops | (same) | single-pass longest-match | 4/4 priority |

The reference solvers are cross-checked against brute force (0 mismatches over 3000
random small instances for word_wrap; exact enumeration for apply_ops). A wrong
frame provably fails, so the fork the harness names and guards is a genuine one.

## Every solution is verified correct (no correctness regression)

| task | model | runs | oracle pass |
|---|---|--:|--:|
| word_wrap | Sonnet 4.6 | 24 | 100% |
| word_wrap | Opus 4.8 | 12 | 100% |
| apply_ops | Sonnet 4.6 | 15 | 100% |

Across all 51 runs, every harnessed solution passed on all discriminating, basic,
and edge cases. The reliability layer is added with full task correctness retained.

## What the harness adds, in the trace

The score is full correctness everywhere; the reasoning the harness installs is the
benchmark's signal. Representative, verbatim from the runs:

- **Correct targeting.** The harness-retrieved operation named the actual failure
  mode on every task: `greedy-without-property` (word_wrap),
  `atomic-TTL-expiry-under-lock` / shared-mutable-without-lock (the cache task), the
  no-rescan adversarial case (apply_ops).

- **Named fork + pre-committed guard + structural falsification** (tooled_proper,
  word_wrap, Opus 4.8):
  > "Falsification test: did I smuggle in a greedy assumption (Suppress: greedy
  > without property)? The inner loop tries every valid j, not just the maximal one,
  > so no greedy shortcut is taken... 0 mismatches across 4000 cases vs brute force."

- **Justified algorithm class** (tooled_proper, word_wrap):
  > "The problem lacks the greedy-choice property, so DP is the justified class...
  > the cost of `words[j:]` depends only on j, never on how `words[:j]` was
  > arranged."

- **Far-pole check before finalizing** (tooled_proper, word_wrap, Opus 4.8):
  > "A draft that drifted to the far pole would have written `(width - used)**3`
  > unconditionally and clamped the oversized line's cost instead of its validity...
  > The differential test specifically stresses oversized words and forced splits,
  > and it passes, confirming I held the reading of each edge case."

Each of these is a checkable claim a runtime monitor or audit can act on, which a
bare answer does not provide.

## Reproducibility

Specs and oracles are self-contained and deterministic. The submitted solutions are
included under `results/` as evidence; re-running `run.py` reproduces every number.
The harness's reasoning discipline reproduced across both models tested and is the
natural axis to extend to more.
