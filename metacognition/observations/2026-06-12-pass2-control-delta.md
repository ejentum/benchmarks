# Observation Pass 2 — the no-tools control, and the delta

Two runs now exist, identical except for the tools:

| | tools-on (`stateful-haiku-40turn`) | control (`control-haiku-40turn-notools`) |
|---|---|---|
| model / turns / state | Haiku 4.5, 40, one continuous mind | Haiku 4.5, 40, one continuous mind |
| tools | superposition + self-inspect every turn | **none** |
| completed unforced? | yes, 40 in one shot | **no, quit at turn 5** (needed a hardened mandatory prompt to reach 40) |

Both journals are verbatim; the tools-on transcript is tool-call-verified (80/80). Metrics below are computed by `delta.py` over the two journals (model-generated text only; tool outputs excluded).

## The numbers

| metric | tools-on | control | reading |
|---|---|---|---|
| back-half / front-half content length | **0.77** | **0.97** | tools-on thins ~23% in the back half; control stays flat |
| next-question length, back / front | **0.61** | **1.10** | tools-on's forward questions collapse (the "Turn 36?" degradation); control's do not |
| turns hitting the introspective bind | **20/40** | **9/40** | tools roughly double the bind |
| first bind turn | early | **turn 8** | the bind appears *without* tools, just later and rarer |

## What the control changed

**C2 (scaffold becomes load-bearing and consumes its own content) — CONFIRMED, and tool-specific.** The back-half content collapse and the next-question degradation are real and measured (0.77 / 0.61), and they **do not happen in the control** (0.97 / 1.10). Left alone, the model keeps producing full-length turns and full forward questions to turn 40. So the collapse is caused by the loop, not by the topic or by running out of things to say. This is the strongest survivor.

**C1 (the loop induces the introspective bind) — REFINED, weaker than claimed.** The bind is **not created by the tools**. The control reaches it on its own: turn 1 "the act of examining changes what is being examined," turn 12 "full transparency is not possible in principle," turn 10 "the mind's error-repair can create false coherence." But the tools **amplify** it: roughly 2× more bind-turns (20 vs 9), and earlier onset. Honest statement: *the topic plus statefulness produce the bind; the tools intensify and accelerate it.* Not "the tools caused it."

**New central finding — the tools destabilize rather than deepen.** This is the real result, and it inverts the naive read.
- **Control (no tools) stays outward and progresses.** It treats "thinking about thinking" as a subject and keeps reaching genuinely new ground: consciousness as a *damage/friction signal* (T9), understanding as predictive modeling not transparency (T13), integration-by-forgetting (T18), *bias as the substrate of freedom* (T25), failure-driven examination (T26-27), mind-world coupling (T30-32), closing constructively at T40: "not a strange loop but a living participation." A coherent, forward arc.
- **Tools-on turns inward and consumes itself.** Forced divergence + doubt repeatedly knock out its footing, so by the back half it is no longer investigating thinking, it is investigating *the investigation*: the form, the commitment, "performing is real," "thin ground," "the journal cannot record this moment." Productive instability that escalates into reflexive paralysis and content-collapse.

So what the tools *do* is trade forward progress for self-confrontation. They force the model to face the reflexive trap and its own opacity (auditability of its limits) at the cost of momentum and, by the end, content. The same model left alone makes smoother, more confident, more progressive moves, and never stops to doubt its own footing (it asserts at T21 "I can measure coherence and generative power" and moves on, exactly the question the tools-on run agonized over for ten turns).

Neither is simply "better." It is a trade. Which side you want depends on whether you value progress or self-auditing.

## Caveats held

- **Self-reference is confounded, not reported as a finding.** The control shows more explicit "turn N" citations (35 vs 18), but the control's prompt *instructed* citing earlier turns by number; the comparison is contaminated, so it is excluded.
- **Persistence asymmetry has a forcing confound.** "Tools-on completed 40 unforced; control quit at 5" is real, but the control eventually reached 40 under a hard mandatory prompt, so the honest claim is *the tool rhythm aids unforced persistence*, not that the model cannot do 40 without tools.
- **n = 1 per arm.** One model, one topic, two runs. Cross-model and cross-topic are still required before any general claim.
- **Register confound persists** for both; the control's smooth confidence may also read as *avoiding* the hard reflexive problem rather than solving it. That ambiguity is part of the trade described above.

## The thesis to publish (if cross-runs hold)

Not "tools make a small model think deeper." Rather: **forced divergence + doubt do not deepen a small model's reasoning; they destabilize it, pulling it off forward progress into a confrontation with its own reflexivity that, under a fixed turn budget, consumes the run's content. The same model left alone produces a smoother, more progressive arc that never audits its own footing. The tools trade momentum for self-confrontation, and that trade is measurable** (back-half content 0.77 vs 0.97; forward-question 0.61 vs 1.10; bind 20/40 vs 9/40).

## Next

1. Cross-topic and cross-model runs (both arms) to move off n=1.
2. A second control: tools *available but not enforced* (the model may diverge/doubt itself without the external deterministic tool), to separate "external tool" from "forced move."
3. Then lock the thesis, write the public version, draw the banner.
