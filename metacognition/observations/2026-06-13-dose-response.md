# Dose-response: Sonnet at 0 / 2 / 4+4 tool calls, blind-judged

Three Sonnet runs on the same question ("what is actually happening when a mind examines its own thinking?"), identical except for tool dose:
- **0** — no tools (`sonnet-0tool-40turn`)
- **2** — selective, model-chose when (the clean run; `sonnet-selective-40turn`)
- **4+4** — forced budget of 4 paired checkpoints, one per quarter (`sonnet-4plus4-40turn`)

Judged by **3 independent judges**, each reading all three runs, run order **rotated** between judges so each run sat in each position exactly once (kills position bias). Judges told to score reasoning quality only and ignore tool markers.

## Result (labels mapped back from the rotation)

| Run | Judge 1 | Judge 2 | Judge 3 | Avg rank |
|---|---|---|---|---|
| **2 calls (selective)** | 1st | 1st | 1st | **1.00** |
| 0 calls (no tools) | 3rd | 2nd | 2nd | 2.33 |
| **4+4 (forced, 8 calls)** | 2nd | 3rd | 3rd | **2.67** |

**Order-invariant: the 2-call run won 1st from all three judges regardless of position.** The dose-response is an inverted-U peaking at ~2 selective calls; **4+4 finished last, below the no-tool baseline.**

## Why 4+4 lost (the judges converged, unprompted)

The forced, scheduled checkpoints made the 4+4 run **stage** its self-corrections instead of having them:
- Judge 3: "Its Checkpoint revisions repeatedly walk back claims it overstated one turn earlier, **manufacturing its own error-catching** … the climactic inversion is asserted with rhetorical flourish rather than argued."
- Judge 2: "Its self-corrections are weaker than they advertise … **cosmetic softenings** that converge on conclusions it had already reached, so its big finish recycles earlier insight under the banner of breakthrough."
- Judge 1: still ranked it 2nd, but on the same axis (a few revisions "arrive pre-packaged as tidy REVISED CLAIM blocks rather than emerging from struggle").

The 2-call run, by contrast, fired at the **one genuine knot** it hit (the unity-of-consciousness problem) and produced a *real* reversal all three judges singled out (Turn 15: "I argued too quickly that unity is 'illusion'").

## Conclusion — this refutes "4+4 is the ratio"

It is **not about the count** (2 vs 4 vs 8). It is **chosen-at-a-genuine-knot vs forced-on-a-cadence.**

- Forcing tool use at *any* cadence underperforms letting a capable model reach for the tool itself. Every-turn (Haiku) was catastrophic (lost 35–5); a moderate forced 4+4 (Sonnet) is the milder version of the same failure — it finished below using no tools at all, because the schedule makes the model **manufacture knots and stage corrections**.
- Minimal, **model-chosen, selective** use is the peak. Left to decide, Sonnet fired **twice** and beat the no-tool baseline; forced to fire **eight times** on a schedule, it fell below it.

So the dose-response curve does not say "find the right number of calls." It says: **the value is in the placement, and placement cannot be forced — it has to be a capable model's own judgment of when it is genuinely stuck.** A fixed ratio (4+4) is the wrong control variable; the right one is "fire only at a real knot," which only a capable model can supply, and which, when supplied, is rare (≈2 in 40 turns here).

This closes the dose-response loop and sharpens the locked conclusion: the tools help only as a *selective, self-triggered* aid to a capable reasoner; both extremes of forcing (every-turn, and even moderate scheduled budgets) are net-negative.
