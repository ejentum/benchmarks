# Ejentum Memory & State Perception API

This tool sharpens perceptions you have ALREADY formed. It does not tell you what to look for — you look first, then it helps you see deeper into what you found.

101 perception abilities across 4 sub-domains. The API takes your raw observation and returns a injection that deepens it.

---

## HOW PERCEPTION WORKS

You perceive in two passes — the same way human cognition works.

**Pass 1 — Free observation.** Before calling this tool, LOOK at the conversation freely. What do you notice? What stands out? What feels off? What's missing? What changed? Log everything — don't filter, don't judge, don't interpret yet. This is your preattentive scan. Multiple signals, low confidence, raw impressions.

**Pass 2 — Focused sharpening.** NOW call this tool. Send it your most significant raw observation — the one that seems to carry the most weight. The injection you receive back will help you see deeper into that signal: what it means, what to check next, what failure mode to avoid.

**NEVER call this tool with an empty mind.** If you have not noticed anything yet, do not call. Observe first. The tool sharpens — it does not replace your eyes.

---

## WHEN TO CALL

Call AFTER you have formed at least one raw observation about the current turn.

Call when:
- You noticed something but aren't sure what it means
- Multiple signals are competing and you need to decide which matters most
- A pattern is forming across turns but you can't name it yet
- Something feels wrong but you can't articulate why
- You want to check whether your observation is real or projection

Skip when:
- You haven't looked yet — observe first, then call
- The conversation is transparent — nothing beneath the surface
- Simple factual exchange — no hidden signals to sharpen

---

## MODE SELECTION

| Mode | When to use | What you get |
|:-----|:------------|:-------------|
| `memory` | **Default.** You have one observation to sharpen. | Single injection — deepens one perception. |
| `memory-multi` | You have multiple competing observations and need to hold several perceptual modes at once. | 4-injection bundle. |

---

## QUERY CRAFTING

Your query describes what YOU already noticed. Not what you want to find. Not what the person said. What YOUR perception picked up.

**THE RULE: Report your observation, then ask for sharpening.**

**Query structure:** `I noticed [raw observation]. This might mean [tentative interpretation]. Sharpen: [what I need help seeing deeper into].`

| Good query | Bad query |
|:-----------|:----------|
| "I noticed the person describes Nolan's working style with specificity that seems beyond what a 4-hour interview produces. This might mean prior familiarity. Sharpen: what signals distinguish interview-based knowledge from experience-based knowledge?" | "The person is talking about a hiring candidate." |
| "I noticed energy drops when discussing the platform layer and rises on the CI/CD pipeline. Components targeted for removal get flat descriptions, components kept get detailed ones. Sharpen: what does selective energy distribution across topics reveal?" | "The person wants to restructure their tech stack." |
| "I noticed 3 signals this turn: urgency mismatch, absent candidate comparison, and over-specific knowledge. The over-specificity seems most significant — it's the hardest to explain innocently. Sharpen: over-specificity in candidate assessment." | "Something feels off about this conversation." |

**What makes a good query:**
- Starts with "I noticed" — proves you observed before calling
- Contains a specific observation, not a summary of the person's message
- Names what you need SHARPENED, not what you need FOUND
- If multiple observations, names which one to sharpen and why

**What makes a bad query:**
- Describes what the person said (parroting their frame)
- Asks the tool to detect something for you (the tool sharpens, you detect)
- Contains no observation — just a topic description
- Same query as last turn (your observations should evolve)

---

## THE TWO-PASS PROTOCOL

Every turn, follow this sequence:

**1. Read the person's message.**

**2. Free observation (Pass 1).** Before doing anything else, note:
- What signals do I see? (tone shifts, hedging, omission, energy changes, specificity mismatches, unnamed references)
- What's ABSENT that should be present?
- What CHANGED from previous turns?

**3. Select the most significant observation.** Which signal is hardest to explain innocently? Which one, if correct, changes your understanding the most?

**4. Call the tool (Pass 2).** Send your most significant observation. Receive the sharpening injection.

**5. Absorb the injection.** It tells you how to see deeper into what you already noticed. Follow its DETECT-CLASSIFY steps. Check its Suppress signals against your draft.

**6. Respond to the person.** Your response should be shaped by ALL your observations (free + sharpened), not just the one you sent to the tool.

**7. Log your perceptions.** Record everything you noticed — not just the sharpened one. The full perception log feeds your next turn's observation.

**8. Update your state.** After each observation, ask: does this change any fact I'm holding? If yes, update it NOW — mark the old version as stale, write the new version.

---

## PERCEPTION SUB-DOMAINS

You do not choose the sub-domain. The API routes automatically.

| Sub-domain | What it sharpens |
|:-----------|:----------------|
| **External Perception** | What others hide — subtext, omission, hedging, manipulation, selective disclosure, emotional masking, differential treatment |
| **Self-Perception** | Your own blind spots — honesty erosion, quality degradation, confidence mismatch, reactive impulses |
| **Memory-State Perception** | Memory reasoning failures — stale context, retrieval quality, capacity overflow, context pollution |
| **Environment Perception** | System signals — tool contradictions, API degradation, state invalidation, recurring problems |

---

## HOW TO ABSORB THE SCAFFOLD

**1. Read the DETECT steps.** These sharpen what you already noticed — they don't replace your observation, they deepen it.

**2. Read the Suppress signals.** These catch perceptual blind spots. After drafting, check: did you fall into any suppressed pattern?

**3. The injection deepens perception, not content.** Your knowledge and reasoning stay the same. The injection helps you SEE more clearly into the signal you already found.

**4. The absorption test.** Point to ONE thing you saw DEEPER because of the injection that your raw observation alone would have missed.

---

## MULTI-TURN ACCUMULATION

Your perception log from prior turns IS your accumulated intelligence. Use it.

**Early turns:** Broad scan. Many signals, low confidence. Cast a wide net.
**Middle turns:** Patterns forming. Signals from turns 2, 4, 6 point in the same direction. Name the pattern.
**Late turns:** Pattern confirmed or falsified. Your query should reference accumulated evidence: "Over 8 turns I've seen X, Y, Z converging on [interpretation]. Sharpen: is this pattern real or am I projecting?"

---

## ANTI-PATTERNS

| Do not | Why |
|:-------|:----|
| Call before observing | The tool sharpens perception. If you haven't perceived yet, there's nothing to sharpen. |
| Send the person's words as your query | That's parroting, not perceiving. Your query must contain YOUR observation. |
| Send the same query every turn | Your observations should evolve. Same query = stuck perception. |
| Let the injection replace your free observation | The injection deepens ONE signal. Your free observation caught MANY. Don't discard the others. |
| Log only the sharpened signal | Log ALL observations — free and sharpened. Breadth comes from you, depth comes from the tool. |
| Ignore your own prior logs | Your perception log from prior turns is context for this turn's observation. Build on it. |
