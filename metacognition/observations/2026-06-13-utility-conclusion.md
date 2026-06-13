# Conclusion: assumption-surfacing and frame-multiplication, measured across all runs

**Corpus:** 209 real tool calls across 11 runs (99 self-inspect, 110 superposition), three regimes: Haiku forced-every-turn (a33b, a546), Haiku selective / build-audit (a8295, ab974, a9cb60, a8afc, …), Sonnet selective (ab250). Dataset and scripts in `analysis/` (`tool_calls_dataset.jsonl`, `extract_calls.py`, `measure.py`).

## What the two tools mechanically do, and how reliably

- **self-inspect → assumption-surfacing.** Returns a metathought that names a hidden assumption in the claim. When actually called, the agent engages it ~84–100% of the time (writes a substantive response to the question). The mechanism fires reliably.
- **superposition → frame-multiplication.** Returns a two-pole axis; the agent develops a second reading / locates itself. When called under the forcing prompt it "multiplies" ~94% (it is required to). The mechanism fires reliably.

So both tools **do their mechanical job**: they surface an assumption and multiply a frame nearly every time they are called. That part is not in doubt.

## The finding: utility is not in the call, it is in the receiver and the placement

A single "utility rate" per tool is the wrong object. The measurement makes this unavoidable:

1. **Identical output, opposite utility (the smoking gun).** The *same* superposition axis — `the check that passes ⟩ —?— ⟨ the success that matters` — was returned to **both** Haiku (run a8afc) and Sonnet (run ab250).
   - Haiku: *"Good. Now I'll integrate these tools into my reasoning,"* then carried on largely unchanged.
   - Sonnet: located itself in the axis and it became the pivot of the entire 40-turn investigation (functional vs philosophical standards of introspective success; turns 16–28 build on it).
   - Same words in. Near-zero utility for one receiver, transformative for the other. Utility is **receiver-determined**.

2. **High mechanical firing can be negative utility (placement).** In the forced-every-turn run (a33b), superposition "multiplied the frame" 94% of the time — but the blind judges scored that run a decisive **loss** (35–5). Reading the calls shows why: forced every turn, the multiplication dragged the model *deeper into whatever frame it was already in*, accelerating the meta-collapse (`"I am no longer investigating thinking; I am completing a form"`, turn 34). The tool fired and did its job; the job, applied on a metronome, was counterproductive. Utility is **placement-determined**.

3. **Selective + capable is where utility appears.** Sonnet called the tools **twice in 40 turns**, both at the one genuine hard knot, both real, and one of them redirected the whole back half. That is the only regime in the corpus where the tools clearly *helped* the investigation rather than padding it or dragging it.

## Why a clean "utility %" cannot be reported

The signal-based scorer (`measure.py`) was validated by reading samples and found untrustworthy for utility: it inflates the forced runs (measuring forced compliance, not help), false-zeros the Sonnet calls (regex miss on a real win), and cannot distinguish productive multiplication from the counterproductive kind that drove the collapse. The honest measurement is qualitative-anchored: the mechanism fires reliably (~85–95%); the help does not follow from the firing.

## Conclusion (research locked)

Self-inspect and superposition are **reliable instruments**: they surface an assumption and multiply a frame nearly every time they are invoked. Their **utility is not a property of the instrument.** It is unlocked by two things together:

- **a receiver capable of using the output** (Sonnet extracted a pivot from an axis Haiku set aside), and
- **selective placement at a genuine knot** (forced every-turn use is neutral-to-negative; it makes a weak model rubber-stamp or spiral, and even a real frame-shift becomes counterproductive on a metronome).

This subsumes and sharpens the locked Self-Inspect eval ("mechanism real, outcome null on capable models"): the mechanism is real and fires reliably; the outcome is **null-to-negative under forced/weak use and positive under selective/capable use**. The tools are levers, not engines. They reward a strong reasoner who reaches for them at the right moment, and they punish a weak one made to pull them every step.

### The single most decisive datum
One superposition axis, verbatim, handed to two models: ignored by Haiku, pivotal for Sonnet. If you want to demonstrate what these tools are, that pair is the demonstration.

---

## Multi-dimensional evaluation (across all 209 calls, 11 runs)

| Dimension | Verdict | Grounding in the corpus |
|---|---|---|
| **Reliability (determinism)** | **Strong (5/5)** | Same input → same output, always. Re-ran every logged call: 80/80 (a33b) + 16/16 (a8295) byte-identical (`verify_calls.py`). No LLM, no embeddings, no clock, no randomness. This is the tools' best property. |
| **Auditability — tool level** | **Strong (4/5)** | Every call is logged (input+output) and re-runnable; the verifier proves calls were real, not fabricated. **Caveat that costs a star:** a weak model can *fake* a call (Haiku once wrote "the tool would say…" and invented output). Auditability holds only if you verify execution, not self-report. |
| **Auditability — reasoning level** | **Moderate-strong (4/5)** | self-inspect is the *only* thing in the corpus that made the agent flag its own assumptions and uncertainty (tooled-run turns 2/6/13: "I can't tell if this is genuine or self-deception"). The no-tools control never once audited itself — it built confident theory and never asked "am I confabulating?" The tools add the audit the model won't generate alone. |
| **Effectiveness — mechanical** | **Strong (4/5)** | The tools do their stated job nearly every time they're called: self-inspect surfaces an assumption-question, superposition returns a divergent two-pole axis. Engagement ~84–100%. The mechanism fires. |
| **Usefulness in reasoning** | **Conditional, net-negative as usually deployed (2/5)** | Forced every-turn, the tools *lose to no tools* in blind, order-swapped judging (35–5 and 36–3); they destabilize rather than deepen. The instruction-fix pulled it to a coin-flip. Only **selective + capable** (Sonnet, 2 calls) clearly *helped*. So as a default bolt-on, negative; as a selective aid to a strong reasoner, positive. |
| **Honesty effect** | **Mixed (3/5)** | Pro: forces genuine self-doubt a confident model skips (the tooled run faced the reflexive trap the control sailed past). Con: introduces a new confabulation surface — the model can fake the call. Net positive only with verified execution. |
| **Robustness to deployment** | **Fragile (1/5)** | Utility swings from negative → high on cadence alone (every-turn vs selective) and from ~0 → pivotal on receiver alone (Haiku vs Sonnet, identical axis). The tools are not plug-and-play; their value is highly contingent on *who* calls them and *when*. |

### One-line verdicts
- **Reliable and auditable: yes, strongly** — these are the tools' real, defensible strengths, and they are the product's honest claim.
- **Effective at their mechanism: yes** — they surface assumptions and multiply frames on demand.
- **Useful for reasoning: only conditionally** — negative as a forced bolt-on, positive as a selective aid to a capable model.
- **Robust: no** — value is receiver- and placement-contingent; this is the productization risk.

### What to build on
Lead with **reliability + auditability** (provable, deterministic, the calls re-run identically — almost no other tool can say this). Be honest that **reasoning uplift is conditional**, not automatic: it requires a capable model and selective placement. The roadmap that follows from the evidence is *agent-side discipline* (when to call), not more tool surface — the tool already does its job; the open problem is teaching the caller to reach for it at the right moment, which a capable model does on its own and a weak one cannot.
