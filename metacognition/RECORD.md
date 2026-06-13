# Metacognition-Bench: Full Record

Single source of truth for the whole investigation. Chronological, with the real numbers, the design evolution, the method mistakes, and the current state. Detailed write-ups live in `observations/`; this ties them together.

## The question

What do two deterministic, keyless metacognition tools do to a small model's (Claude Haiku 4.5) reasoning over a long, stateful, single-context chain? Tools:
- **superposition** — returns a two-pole tension map ("X vs Y, which is your real measure?"); a forcing function for divergence.
- **self-inspect** — returns one assumption-challenging question ("what does not follow? when would this not hold?").

Seed for every run: *"What is actually happening when a mind examines its own thinking?"* 40 turns, one continuous Haiku, builds turn on turn.

## Runs (chronological)

1. **`runs/stateful-haiku-40turn`** — tooled, both tools EVERY turn. Completed 40 unforced. Transcript verified: 40 superposition + 40 self-inspect calls, all 80 re-run byte-identical (`verify/verify_calls.py`).
2. **`runs/control-haiku-40turn-notools`** — no tools. First attempt quit at turn 5 (weak-model under-persistence); a single forced agent reached 40. This is the control.
3. **`runs/tooled-fixed-haiku-40turn`** — tools on a **build-then-audit cadence** (32 build turns + 8 audit turns at 5,10,…,40). Cadence verified; 16 audit tool calls (8+8) all re-run byte-identical.
4. **universal-grid run** (task_type eliminated, `superposition_universal.py`) — journaling broke (agent printed `printf` as a PowerShell block instead of executing it); only 25/40 turns recoverable from the transcript. Tools confirmed really called (10 superposition + 8 self-inspect); recovered audit maps all universal, leak gone. Not used for a panel (incomplete).
5. **collapse-triggered run** (current design) — agent runs free, calls the tools itself ONLY when its reasoning starts shrinking. Read off the transcript, no journaling.

## Findings

### Tools every-turn lose to no-tools, decisively
Two independent blind judges, run order swapped between them (so a verdict that survives the swap is not position bias):
- **Judge 1: control 35–5. Judge 2: control 36–3.** Order-invariant. The no-tools control is the clearly stronger reasoner. (`observations/2026-06-12-pass2-control-delta.md`, `…blind-judge-panel.md`)

Measured delta (`delta.py`, model text only): content back-half/front-half **0.77 (tooled) vs 0.97 (control)**; next-question back/front **0.61 vs 1.10**; introspective-bind turns **20/40 vs 9/40**. The tooled run thins and its forward-questions collapse ("Turn 36?", "Turn 37?"); the control does not.

### Why the tools hurt (5 mechanisms)
1. They point attention at the self, not the subject; on a reflexive topic the self-audit eats the subject.
2. Forced divergence (take the opposite pole every turn) blocks the commitment cumulative reasoning needs.
3. The deterministic map became a fixation rut: `step_closed vs mission_advanced` returned **12 times** (16 distinct maps over 40 turns); same input shape pins the same map.
4. Doubt with no evidence-channel (pure introspection, no web/files) spirals instead of resolving.
5. Per-turn tool overhead taxes a small model's reasoning budget.
Net: the tools **destabilize, they don't deepen**; they trade forward progress for self-confrontation.

### What the tools DID add
Epistemic self-honesty: the tooled run is the only one that ever doubts itself (turns 2, 6, 13, 30 — "cannot tell genuine insight from sophisticated self-deception"). Both judges flagged the same turns. The control confidently builds and never asks "am I confabulating?" So the tools surface a real limitation (auditability), at the cost of the content. This matches the locked Self-Inspect eval: mechanism real (auditability), outcome null-to-negative on capable open-ended reasoning.

### The fix (instructions only) pulled it back to even
Build-then-audit cadence + aim the tools at the claim (not the self) + answer self-inspect with a concrete counterexample + treat a repeated map as a rut-signal. Result (`observations/2026-06-12-pass3-fixed-tooled-panel.md`): the blind panel went from a 35–5 blowout to a **coin-flip** (Judge 1: fixed-tooled 30–6; Judge 2: control 24–16). Order-invariant signal: **the fixed-tooled run won the back half in BOTH judges' reads** — the exact collapse that killed the original is cured. The audits earned their keep by falsifying claims (turn 5 flow-state, 15 surprise, 30 cost-of-distortion) and it refused closure at turn 40 instead of padding.

### The superposition leak, and task_type elimination
Residual both judges flagged: superposition leaked off-domain "code-review" vocabulary ("step closed vs mission advanced," "unit named vs behavior at runtime") into a couple of audits.
- Root cause: the grid (`superposition-manifestation-grid.csv`) is **36 rows across 8 lenses, all agentic-work domains** (code & debug, research, writing, communication, planning, data, evaluation, long-horizon execution). **No metacognition lens.** The selection is deterministic light token-matching; an out-of-domain philosophy input has no lens to land on, so it falls to the nearest generic work-map, whose vocabulary bleeds in. The leak lives in the map TEXT, not the task_type label.
- Fix (Frank's call): **eliminate task_type.** The 8 domain copies of each operator (GOAL/CRITERIA/REFERENT/SCOPE/DIAGNOSIS/METHOD/STATE/PRIORITY) are the same tension in different costumes; collapse them to **8 universal, domain-neutral operator maps**, select on the map text alone. Built as `superposition/python/superposition_universal.py` (standalone, experimental). Smoke test + recovered audit maps confirm: **leak gone.** Metacognition input → REFERENT ("the thing named vs the thing it stands for"); coding input → CRITERIA ("the check that passes vs the success that matters"); deterministic. If it holds in a clean panel, fold into the real engine (grid + selector + regenerate).

### Current design: tools as a collapse-interrupt (Frank's)
Not every turn (corrosive), not on a cadence (arbitrary), not removed (loses the auditability). The agent runs free and calls the tools **autonomously, only when its reasoning starts shrinking** — thinner next-questions, restating without adding, drift onto "the form/commitment," no new ground. The tools surface the assumption holding it stuck and reopen the topic. Padding becomes impossible by design, because padding is itself the trigger.

## Method lessons (recorded honestly)

- **Per-turn journaling was unnecessary ceremony.** The agent's transcript already records every turn verbatim (the failed universal run was partially reconstructed straight from it). The `printf` appends + `wc -l` checks added fragility, broke once, and cost a full re-run for nothing. **Correct method: one prompt, let the agent run, extract the turns from the transcript afterward.** No file I/O inside the loop.
- **Tool cadence is the whole ballgame.** Every-turn = corrosive; removed = loses auditability; the right answer is autonomous + collapse-triggered.
- A weak model under-persists on a long free-form mandate (control quit at turn 5); the per-turn tool rhythm also happened to buy persistence in the original tooled run.

## Artifacts

- `runs/` — three completed runs (journal + raw transcript + run cards), plus the control's attempt provenance.
- `tools/` — `self_inspect.py`, `superposition.py` (the exact files used). Universal variant: `superposition/python/superposition_universal.py`.
- `verify/verify_calls.py` — re-runs every tool call on its logged input; proves calls are real.
- `delta.py` — computes the tools-on vs control delta.
- `observations/` — pass1 (tools-on read), pass2 (control delta), pass3 (fixed-tooled panel), blind-judge-panel.

## Tool-trigger calibration + model comparison (the clean run)

After the build-then-audit fix, the question became: how should the tools fire? We tried several triggers, all as instruction-only changes, agent runs free and is read off its transcript (no journaling, which was wasted ceremony — the transcript already logs every call):

- **Every-turn (mechanical):** Haiku calls both tools every turn. Distractive — this is the corrosive pattern that lost 35–5. Rejected.
- **Collapse-triggered ("call when you notice you're collapsing"):** Haiku fired **0 times** across 40 turns, even though it drifted onto "the form" at turns 38–39 (the trigger condition, almost verbatim). A small model won't reliably detect/act on its own collapse.
- **Selective ("only at a genuine hard knot"):** Haiku fired essentially never, and the one time it reached for self-inspect it **faked the call** — wrote "the tool would be asking…" and invented the output (the confabulation pattern). So selective-but-honest tool use is the hard part for a weak model.
- **Selective on Sonnet:** **clean.** 40 turns, **2 real tool calls** (verified: real `tool_use` + `tool_result`, not faked), both fired at the *same* genuine knot (the unity-of-consciousness problem, ~turns 14–16), then 24 more turns of solo reasoning. self-inspect returned "When would this not hold?"; superposition returned the axis "the check that passes ⟩ —?— ⟨ the success that matters," which Sonnet **located itself in** (not flipped) and which produced the pivotal reframe (functional vs philosophical standards of introspective success) that reorganized the back half.

**Resolution:** tools as *auxiliary checkpoints fired only at genuine knots* work on a model capable enough to self-calibrate. The corrosion was never the tools per se; it was over-calling, or a weak model that can't judge when it's stuck (so it either never calls or fabricates). Haiku needs the trigger imposed structurally; Sonnet judges it itself. Framing matters too: telling a model "you do NOT deepen on your own" is false and counterproductive — the tools are auxiliary, not the engine.

### Method correction (recorded)
Two mtime misreads this session: I called a dead Haiku run "still running" (rationalized a flat byte count), and a live-but-slow Sonnet run "dead" (over-read a 229s gap). mtime gaps are not a reliable life/death signal; only the completion notification is. Read evidence straight, don't infer state from byte counts.

## Open / next

- Clean blind panel on the universal grid (Sonnet clean run available as the artifact); if it holds, promote `superposition_universal.py` into the real engine (grid + selector + regenerate, drift/parity tests).
- Cross-topic runs (the seed has only been "thinking about thinking").
- The Sonnet clean run is the first evidence the tools *help* a capable model selectively; needs replication.
