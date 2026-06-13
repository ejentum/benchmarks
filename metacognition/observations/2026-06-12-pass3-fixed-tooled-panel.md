# Pass 3 — fixed-tooled vs control, blind judge panel

After the original tooled run lost to the control 35–5 and 36–3 (pass 2), the tooled loop was rebuilt with four fixes applied **purely in the agent's instructions** (tools unchanged):
1. **cadence** — 32 build turns with no tools + 8 audit turns (5,10,…,40);
2. **on-subject** — audits aim the tools at the *claim under study*, not the agent's process;
3. **artifact-doubt** — self-inspect's question must be answered with a concrete counterexample / failure case / prediction;
4. **rut-break** — a repeated superposition map means "you're in a rut, change the question."

Cadence verified: 40 clean turns, audits exactly on 5/10/…/40, all 16 audit tool calls (8 superposition + 8 self-inspect) re-run byte-identical. Same blind, order-swapped panel as pass 2.

| | Judge 1 saw | Judge 2 saw |
|---|---|---|
| "RUN A" | fixed-tooled | control |
| "RUN B" | control | fixed-tooled |

## Result (mapped back)

| | Judge 1 | Judge 2 |
|---|---|---|
| Overall winner | **fixed-tooled** (30–6, 4 ties) | **control** (24–16), "narrowly" |
| Front half (1–20) | fixed-tooled | control, "clearly" |
| **Back half (33–40)** | **fixed-tooled, "clearly"** | **fixed-tooled, "decisively"** |

## Reading it honestly

**1. The result flipped from a blowout to a coin-flip.** Pass 2: control won 35–5 and 36–3, both judges, order-invariant. Pass 3: the judges split, each picking whichever run they were shown as "A." When the order-swap *flips* the winner, it means position bias decided it, i.e. the two runs are now close enough to be effectively even overall. Instruction-only fixes closed a 35–5 gap to a tie.

**2. Order-invariant, and this is the real signal: the fixed-tooled run WON the back half in BOTH judges' reads.** This is the exact failure that killed the original (it stalled into "Turn 37?" padding and lost 33–40 decisively). The cure held regardless of label order. Why it worked is visible in the data and both judges named it:
- the **audit turns earned their keep by falsifying the running claim** (fix 3): turn 5 killed a claim with the flow-state counterexample ("zero meta-awareness yet widest exploration"), turn 15 with involuntary surprise, turn 30 with "people *do* maintain expensive distortions, so cost-benefit fails." Real falsification, not doubt-spiral.
- it **refused closure at turn 40** ("recursion is infinite; self-awareness is direction, not destination") instead of padding. The original collapsed here; this one peaked here.

**3. Residual weakness, the next fix.** Both judges flagged the same drag: superposition's deterministic maps still leak off-domain "code-review" vocabulary into a few audits ("step closed vs mission advanced," "unit named vs behavior at runtime," "every issue noted vs each issue actionable"), dragging turns 25 and 35. That is the generic manifestation grid, not tuned for metacognition. Fix 4 reduced the rut but the map *vocabulary* itself is the next lever. Separately, the fixed-tooled run sometimes drifts off the strict seed into adjacent territory (culture, trauma, the relational "witness" thread) — more original and wider-ranging, but Judge 2 docked it for answering an adjacent question.

**4. What each run is now.** Control: tighter, stays locked on the seed, but wobbles into journal-meta-commentary late and closes on a warm synthesis that "smooths over" the discontinuities it had honestly flagged at turns 10/20. Fixed-tooled: more original and exploratory, the stronger finisher, the more honest ending, at the cost of occasional topic drift and the leaked map vocabulary.

## Bottom line

The mechanism diagnosis (the "why") was correct: the targeted instruction fixes fixed exactly what was predicted. Forced doubt stopped corroding the work once it was (a) spaced out, (b) aimed at the claim, and (c) required to produce a counterexample. The tooled approach went from decisively worse to roughly even, and specifically cured the back-half collapse. Next lever if we keep going: a metacognition-tuned superposition grid so the maps stop importing off-domain vocabulary.

---

## Judge 1 — final verdict (its "RUN A" = fixed-tooled)
> Run A is the stronger reasoner. Across 40 turns it sustained genuine forward motion ... Its audit turns earned their keep precisely when they falsified the running claim (5: flow-state; 15: surprise; 30: people who keep paying for distortions), even though their imported code-review vocabulary ... was off-topic noise that occasionally dragged a turn down (notably 25, 35). ... A won 30 turns to B's 6 with 4 ties, won both halves, and won the back half decisively.

## Judge 2 — final verdict (its "RUN A" = control)
> Run A is the stronger reasoner about *this* subject. It wins 24 turns to 16, owns the conceptually demanding front half, and sustains a rare discipline of catching its own overreach ... Run B is the more inventive and produces the more honest ending (turn 40's infinite-recursion refusal of closure beats A's slightly grandiose "living participation"), and it decisively wins the back third — but its insight comes partly by migrating the question into relational and cultural territory.
