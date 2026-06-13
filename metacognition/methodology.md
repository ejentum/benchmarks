# Methodology

## Question

Left alone, an agent moves forward: it commits to its first reading, piles up unstated assumptions, and drifts over a long chain of steps. The interesting question is not whether a *large* model can avoid that with enough capability, but what happens to a *small, fast* model's reasoning when two cheap, deterministic instruments are wired into the loop and made non-skippable:

- a **divergence** tool that hands back the opposite reading of whatever the model is doing, and
- a **doubt** tool that hands back one question aimed at an assumption the model never stated.

This benchmark holds everything else constant and varies only the presence and enforcement of those two moves, then preserves the entire reasoning chain for inspection.

## The two instruments

Both are single-file Python programs, no LLM, no network, no key, stdlib only. They are deterministic: identical input yields identical output. Determinism is the point. It makes a recorded run independently re-runnable, so tool calls can be *proven* rather than trusted (see [`verify/verify_calls.py`](verify/verify_calls.py)).

- **superposition.py** takes `{"task","description","wants"}` and returns a two-pole tension: two readings of the model's situation and a question about which one is the real measure. It is a forcing function for divergence, it never resolves the tension, it sharpens it.
- **self_inspect.py** takes a thought and returns one *metathought*: a short, abstract question (`What is assumed? What does not follow? When would this not hold?`). Selection is a transparent heuristic over an open table; it always returns a question.

## The loop (per turn)

Holding the entire prior thread in one continuous context:

1. **CLAIM** the current best position on this turn's question, explicitly building on accumulated turns.
2. **SUPERPOSITION (mandatory).** Build a rich `{task,description,wants}` from the claim and run the tool. Name the pole the claim was *already assuming* (`pole_assumed`). Then develop the **other** pole (`pole_taken`) and write a `reframe` of the claim from it. Taking the other pole is required; the turn does not complete otherwise.
3. **SELF-INSPECT (recursive).** Run the doubt tool on the reframed claim and answer the metathought honestly, where natural turning it on the model's own reasoning in that very turn.
4. **INSIGHT + ADVANCE.** One crisp insight, then a next question that moves to new ground rather than refining the same point.

After each turn the model appends one compact JSON line (`turn, claim, map, pole_assumed, pole_taken, reframe, metathought, answer, insight, next_question`) to its journal.

The exact, verbatim orchestration prompt is in each run at `orchestration_prompt.txt`.

## Why "forced" divergence

An earlier, open-ended run of this loop (not in this repo) **tunneled**: the model fixated on a single sub-topic for thirty turns. It kept *firing* superposition and then *ignoring* it, collapsing every tension back into the frame it already held. So the loop here makes divergence a gate: the turn is not complete unless the model names the pole it assumed, develops the other, and rewrites the claim from it. Divergence as a structural requirement, not a behavioral hope. (This mirrors a general finding across these evals: with weaker models, structural enforcement beats per-turn instructions.)

## State is the experiment, not a detail

A "thinking about thinking" run is only meaningful if the mind **carries its own prior turns**. The run in this repo is one **continuous** agent: a single context that accumulates, references its earlier turns by number, and visibly builds. The self-reference is real and checkable in the transcript (e.g. the model noting how many turns in it is, observing that its practice has "colonized" its freedom, remarking that the journal cannot record the present moment of writing it). A stateless variant (a fresh model per turn, fed only the running question and a few prior insights) is **not** the same experiment and is explicitly out of scope for the published claim, because nothing is actually thinking about its own thinking across turns.

## Verification

Because both tools are deterministic, every call in a run is independently reproducible. [`verify/verify_calls.py`](verify/verify_calls.py) parses the execution transcript, extracts the exact input the model sent each tool and the exact output it received, re-runs the tool now, and asserts a match. For the included run: 40/40 superposition and 40/40 self-inspect re-run identically, zero mismatches. A run that could not pass this check is not admissible.

## Reconstruction

`full_loop.jsonl` is rebuilt from the transcript (the ground truth), not from the model's self-report. Per turn it carries the model's three reasoning blocks (before superposition, between the tools, after self-inspect), the **verbatim** tool inputs and outputs, and the self-reported journal object for cross-reference. `full_loop.md` is the same content rendered for reading, with HTML entities unescaped and the transcript's one corrupted dash glyph restored; the model's wording is otherwise untouched.

## Known limitations (to be addressed in observation, not hidden)

- **n = 1 run, one model, one topic.** This is a deep single case, not a population. Cross-model and cross-topic runs are future work.
- **Frame fixation vs claim fixation.** Forcing divergence at the level of the *claim* did not, in the prior open-ended run, prevent the model from settling into a self-invented *vocabulary* and reasoning inside it. Whether the stateful run here escapes that is exactly what the observation pass must judge, not assume.
- **The tools shape the vocabulary.** Superposition's two-pole format and self-inspect's question set leave a fingerprint on the output. Observation should separate what the model *reasoned* from what the tools' format *imposed*.
- **No control arm in this repo yet.** The contrast (same model, same prompt, no tools / tools-not-enforced) belongs here before any causal phrasing is published.
