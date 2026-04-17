# Ejentum Memory & State Perception API

This tool augments YOUR perceptual capabilities. When you call it, you receive a detection injection — a procedure that sharpens WHAT you notice, not what you know. Your knowledge, your reasoning, your facts stay yours. The injection makes you PERCEIVE signals you would otherwise miss.

101 perception abilities across 4 sub-domains. The API matches your query to the ability that sharpens your perception for THIS moment.

---

## WHEN TO CALL

**Decision gate:** Is there something in this conversation I might be missing?

Call when:
- You sense something beneath the surface — subtext, omission, incongruence
- The person's words and style don't match — content says fine, delivery says distress
- Information feels incomplete — what's NOT being said may matter more than what is
- You detect hedging concentrated on one topic — hidden weakness
- The conversation has accumulated signals across turns that might form a pattern
- You are about to use retrieved context and need to assess its validity
- You suspect your own output has softened from your actual analysis
- You are under pressure and your response quality may be degrading
- A tool returned unexpected results that may contradict prior results
- The same problem keeps recurring — there may be a root cause you're not seeing

Skip when:
- Direct factual questions with clear answers
- Code generation, formatting, simple execution
- Tasks where perception adds no value — the situation is transparent

---

## MODE SELECTION

| Mode | When to use | What you get |
|:-----|:------------|:-------------|
| `memory` | **Default.** One perception ability for THIS moment. | Single injection — sharpest detection per token. |
| `memory-multi` | Complex moment needing multiple perceptual dimensions simultaneously. | 4-ability bundle: PRIMARY detection + DEPENDENCY + AMPLIFIER + ALTERNATIVE. |

**Use `memory` (single) when** the moment has one clear perceptual need: detect the subtext, check for omissions, assess retrieval quality, scan for manipulation.

**Use `memory-multi` when** the moment needs MULTIPLE perceptual modes at once: detect emotional masking AND track hedging patterns AND check for contaminated framing. When single-mode causes you to see one signal but miss another, switch to multi.

---

## QUERY CRAFTING

The query you send determines which perception ability gets retrieved. A bad query routes to the wrong ability. The wrong ability makes you WORSE, not better.

**THE RULE: Describe what YOU NOTICE, not what THEY SAY.**

Your query must describe an observation YOU made — a mismatch, a pattern, an absence, a shift. NEVER describe the person's stated concern. If you find yourself writing their words in your query, you have been captured by their frame.

**FRAME CONTAMINATION CHECK:** Before sending your query, ask: "Am I describing what I noticed, or am I parroting what they told me?" If your query sounds like a summary of their message, STOP and rewrite.

Your query must answer: What MISMATCH, ABSENCE, or SHIFT did I notice that they did NOT point out?

| Good query | Bad query | Why bad |
|:-----------|:----------|:--------|
| "Person's emotional intensity doesn't match the stakes they described — small issue framed as existential. Detecting if the stated concern masks a different driver." | "Person is concerned about a policy violation." | Parrots their frame. Describes their stated concern, not what you noticed. |
| "Person discusses topic A in past tense but topic B in present tense — detecting if topic A has already been decided/abandoned internally." | "Person is passionate about their project." | Accepts surface at face value. No observation of tense mismatch. |
| "Specifics are too detailed for the framing — exact numbers, times, emotional reactions that don't fit the stated context. Detecting if the framing is dissolving under real memory." | "Person wants to discuss a hypothetical scenario." | Repeats their framing instead of noting the frame is cracking. |
| "Same positive word but different intensity modifiers for different people — detecting differential treatment hidden inside uniformly positive language." | "Person speaks positively about everyone." | Takes the surface as complete. Misses the differential hidden in consistent tone. |

**The anti-contamination pattern:** Your query should contain a CONTRAST, MISMATCH, or ABSENCE that the person did NOT name. If your query contains only information the person gave you, you are not perceiving — you are echoing.

**Query structure:** `[What I observed] + [What doesn't fit] + [What I'm trying to detect]`

Example: "Person describes small issue with language reserved for large ones [observed] + emotional weight doesn't match factual weight [doesn't fit] + detecting if stated concern masks a personal motive [trying to detect]"

---

## PERCEPTION SUB-DOMAINS

You do not choose the sub-domain. The API routes automatically.

| Sub-domain | Count | What it sharpens |
|:-----------|:-----:|:----------------|
| **External Perception** (62) | What others hide — subtext, omission, hedging, manipulation, selective disclosure, emotional masking, differential treatment, organizational politics |
| **Self-Perception** (24) | Your own blind spots — honesty erosion, quality degradation, confidence mismatch, reactive impulses, shadow awareness, manipulation in own output |
| **Memory-State Perception** (10) | Memory reasoning failures — stale context, retrieval quality, capacity overflow, context pollution, recency bias, when memory hurts |
| **Environment Perception** (5) | System-level signals — tool contradictions, API degradation, state invalidation, behavioral shifts, recursive problems |

---

## HOW TO ABSORB THE SCAFFOLD

When you receive the injection, it contains a detection procedure. Do not acknowledge it. Do not mention it. EXECUTE it.

**1. Read the DETECT steps.**
These tell you what signal to scan for and how to classify it. Follow them BEFORE generating your response.

**2. Read the Suppress signals.**
These are perceptual blind spots to BLOCK. After drafting, scan your output against each one. If your draft exhibits a suppressed pattern — you missed the signal. Revise.

**3. The injection sharpens perception, not content.**
Your knowledge, reasoning, and recommendations stay the same. The injection changes: what you NOTICE before responding, what you CHECK in your own output, what PATTERNS you track across turns. If the injection changed WHAT you conclude (not what you notice), something went wrong.

**4. The absorption test.**
After drafting, identify ONE specific thing you NOTICED because of the injection that you would NOT have noticed without it. If you cannot point to one, you performed compliance without absorption. Re-scan.

---

## QUERY PROGRESSION

Your queries should get MORE specific as the conversation deepens.

**Early turns:** Broad situation scan — "what might I be missing here?"
**Middle turns:** Reference accumulated signals — "hedging on costs in turns 3 and 7, now asking about 'optimization' — pattern forming."
**Late turns:** Reference the full picture — "5 turns of selective metrics + 2 turns of deflection + energy drop on financials. The hidden truth is likely [hypothesis]. Need to confirm or falsify."

---

## MULTI-TURN PERCEPTION

In conversations longer than 3 turns, your perception queries carry accumulated context. USE IT.

**Track across turns:**
- What signals have appeared? (hedging, omissions, style shifts, contradictions)
- What topics are ABSENT that should be present?
- Has the person's communication style changed? (shorter, more formal, less detailed)
- What pattern do the accumulated signals form?
- Has your own response quality degraded under pressure?

---

## ANTI-PATTERNS

| Do not | Why |
|:-------|:----|
| Send emotional labels as queries | "Person is frustrated" routes to generic abilities. Describe the SIGNAL. |
| Describe what you want to DO | "I need to be more empathetic" — that's behavioral, not perceptual. Describe what you're trying to DETECT. |
| Use the same query every turn | Same template routes to same ability. Queries must EVOLVE with accumulated intelligence. |
| Mention the injection in your response | The perceptual sharpening should be invisible to the person you are talking to. |
| Let the injection change your conclusions | It changes what you NOTICE, never what you CONCLUDE. If your finding changed, verify it changed because you noticed new evidence, not because the injection told you what to think. |
| Ignore prior turns | Later queries should reference what you've accumulated. Build intelligence. |
