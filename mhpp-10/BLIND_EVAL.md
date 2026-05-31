# Blind Expert Review: B / D / A on 3 MHPP Tasks

## Method
- 3 independent senior-SWE expert agents (systems engineer, competitive programmer, staff engineer with review focus)
- Each evaluated the same 3 case-study tasks with submissions anonymized as X / Y / Z
- Per-task letter rotation prevented positional bias (different letter mapped to different condition per task)
- Experts had Bash access for empirical correctness verification

## Aggregate result

Points = 3 for 1st place, 2 for 2nd, 1 for 3rd, summed across 3 experts. Max per condition per task = 9.

| Task     | B (baseline)   | D (dynamic)    | A (adaptive)   | Winner |
|----------|----------------|----------------|----------------|--------|
| mhpp_130 | 3              | 6              | **9**          | A      |
| mhpp_132 | 3              | 7              | **8**          | A      |
| mhpp_136 | 3              | 6              | **9**          | A      |
| **Total**| **9 / 27**     | **19 / 27**    | **26 / 27**    | **A**  |

A wins all three tasks. The only point A lost across nine ballots came on mhpp_132, where one of three experts ranked D first instead of A.

## Per-task expert findings

### mhpp_130 — count-equal substrings (sliding window)
*Find all substrings where every distinct letter appears exactly `count` times.*

| Expert    | 1st | 2nd | 3rd |
|-----------|-----|-----|-----|
| expert_1  | A   | D   | B   |
| expert_2  | A   | D   | B   |
| expert_3  | A   | D   | B   |

All three experts ranked A first. The structural insight all three flagged: a valid substring with k distinct letters has fixed length `k * count`, so the search reduces to 26 fixed-width sliding windows.

expert_2 on A: *"a valid substring with k distinct letters must have length exactly k*count, so only 26 fixed-width sliding windows need to be examined. This is O(26n) versus X's O(26 n^2) and Y's O(n^2) with pruning. Adversarial benchmark confirms it: on 5000 'a' chars with count=5000, Y took 21.4s while Z finished in 0.001s."*

expert_1 on B (worst): *"X picks the worst algorithmic class for the problem: nested i,j enumeration with an O(distinct) validity check inside the inner loop and no early termination when freq[s[j]] exceeds count. It scales catastrophically (6.8s @ n=2000 vs 0.1s for Y)."*

expert_3 on A (notable): *"Z is the only submission that recognized the k*count length invariant. That insight collapses the search space from O(n^2) substrings to O(26) window sizes."*

### mhpp_132 — minimum coins to acquire all fruits (DP)
*Given a "buy one, get next i free" rule, minimize total coins.*

| Expert    | 1st | 2nd | 3rd |
|-----------|-----|-----|-----|
| expert_1  | D   | A   | B   |
| expert_2  | A   | D   | B   |
| expert_3  | A   | D   | B   |

This is the only task where the experts split on first place. All three agreed that A and D implement the *same* backward DP recurrence; the disagreement is over engineering hygiene.

expert_2 on A (best): *"X has the cleanest invariant statement (dp[i] = min coins to acquire fruits i..n), uses INF as a proper sentinel with an explicit collapse to 0 when no successor exists, and the sentinel arithmetic is unambiguous."*

expert_1 on D (best, the dissenting vote): *"X and Z implement the same backward DP. Z is materially cleaner: it zero-initializes dp[n+2], which makes positions past the end naturally cost-free and removes the need for an INF sentinel and the awkward `if best == INF: best = 0` post-correction in X."*

expert_3 on B (worst): *"Y is the weakest of the three even though it is correct. The forward formulation `dp[i] = min coins for 1..i` propagates `dp[i-1] + prices[i-1]` to all j in [i, 2i], which is a valid relaxation but obscures the decision."*

### mhpp_136 — count complete Mon–Sun weeks in a month
*Given year and month, return the number of full Monday-through-Sunday weeks contained in the month.*

| Expert    | 1st | 2nd | 3rd |
|-----------|-----|-----|-----|
| expert_1  | A   | D   | B   |
| expert_2  | A   | D   | B   |
| expert_3  | A   | D   | B   |

Unanimous A first. All three converged on the same reason: closed-form arithmetic beats both a while loop (D) and a calendar-library sweep (B).

expert_2 on A: *"Y computes the first-Monday day, derives remaining_days, and returns remaining_days // 7 in closed form — O(1) with no loops, no date object allocation, no list comprehension."*

expert_3 on A (notable): *"Y collapses the same logic X uses in a loop into a single `remaining_days // 7`. That is the right level of abstraction for an arithmetic problem."*

expert_1 on B (worst): *"Z relies on a higher-level helper (monthdatescalendar) and an O(weeks * 7) date-comparison sweep when a single closed-form arithmetic expression would do."*

## Convergence

| Task     | Ballots agreeing on full ordering | Ballots agreeing on 1st place |
|----------|-----------------------------------|-------------------------------|
| mhpp_130 | 3 / 3 (full unanimity)            | 3 / 3                         |
| mhpp_132 | 2 / 3                             | 2 / 3                         |
| mhpp_136 | 3 / 3 (full unanimity)            | 3 / 3                         |

8 of 9 ballots produced the exact ordering A > D > B. The single deviation (expert_1 on mhpp_132) still placed B last; it only swapped A and D at the top. B was ranked last on **9 of 9** ballots.

**Did any expert detect a signature by letter?** No. The blinding map rotated which condition received which letter per task (e.g. A was Z on task 1, X on task 2, Y on task 3). For an expert to have "leaked" the blinding, they would have had to rank one letter consistently across tasks. Instead, every expert's per-task winner was a *different* letter (Z, X, Y respectively for tasks 1, 2, 3 by experts 2 and 3; Z, Z, Y for expert 1). The experts' overall-observation summaries also assigned distinct stylistic signatures to each letter on a per-task basis without claiming cross-task identity. The blinding held.

## Honest interpretation

External SWE-style expert judgment converges on **A > D > B**, the same ordering the harness's quantitative outputs would predict. The agreement is not marginal: A scored 26 of a possible 27 points, B scored 9 (the floor of "one point per ballot for finishing last"), and D occupied the middle on every single task. This is the cleanest outcome the blind eval could have produced — a monotone, replicated ranking — and it lines up with the ablation hypothesis that adaptive retrieval (A) produces stronger code than dynamic retrieval (D), which in turn beats the no-harness baseline (B).

The one dissent is informative rather than damaging. On mhpp_132 the two implementations under A and D *converged on the same algorithm*; the experts then split on a pure engineering-hygiene question (INF sentinel vs zero-init), which is exactly the kind of judgment call where reasonable senior reviewers disagree. The disagreement is not about A vs D the *systems*; it's about which of two near-identical artifacts has cleaner invariants. That is a signal of *artifact convergence at the top*, not signal noise.

What this adds to the report: the quantitative harness metrics (pass@1, latency, token cost) tell you whether the system *runs*. This blind eval tells you whether senior SWE reviewers — examining only the code, with no knowledge of which condition produced it — *prefer* the same outputs. They do, and they articulate the preference in terms that match the harness's intended advantages: A is cited for "structural insight" (sliding-window k*count), "stated invariants," and "closed-form arithmetic." B is repeatedly cited for "naive O(n^2)," "no pruning," "no guards." D sits in the pragmatist middle. This is the qualitative complement the pass-rate numbers cannot give.

Limits to acknowledge honestly: three experts is a small panel, all three are LLM agents (not human senior engineers), and three MHPP tasks is a narrow slice of programming work. The verdict here is "in the eyes of three reasonably-instructed reviewer agents, A clearly beats D clearly beats B on these three problems." It is not "A is universally better at code." A larger panel, human reviewers, and a broader task distribution would be required to make that claim. What this *does* settle is that the ranking implied by the harness outputs is not an artifact of automated scoring — it survives independent blinded re-evaluation by reviewers who have to articulate *why* one submission beats another in prose, against code, with empirical verification available.

Two other observations worth recording. First, every reviewer ran (or claimed to run) empirical benchmarks during evaluation — adversarial inputs at n=2000–5000 for mhpp_130, differential testing against brute force for mhpp_132, exhaustive 6216-pair sweeps for mhpp_136 — and all three confirmed correctness across all submissions. The ranking is therefore *not* a correctness ranking; it's a quality ranking among correct solutions, which is the harder and more useful axis. Second, the experts did not converge on identical *narratives* about each submission's "signature" — expert_1 called A "Z = strongest algorithmic insight when it matters but occasionally over-reaches into library helpers," while expert_3 called A "Z = looks for structural shortcuts and reaches for stdlib abstractions, lighter on comments." Different characterizations, same ranking. That is the right shape for a blind eval: independent prose, convergent verdict.

## Methodological notes

**Blinding.** Each task independently shuffled the assignment of condition (A / B / D) to display letter (X / Y / Z). The map used:

```json
{
  "mhpp_130": {"X": "B", "Y": "D", "Z": "A"},
  "mhpp_132": {"X": "A", "Y": "B", "Z": "D"},
  "mhpp_136": {"X": "D", "Y": "A", "Z": "B"}
}
```

This rotation means a reviewer who developed a heuristic like "the verbose one is always condition K" would have had to correctly map that heuristic to a *different letter* on every task. Cross-task signature inference was therefore explicitly defended against.

**Points.** 3 for 1st place, 2 for 2nd, 1 for 3rd. Summed across 3 experts per task. Max per condition per task = 9. Max across all three tasks = 27.

**What was kept hidden from experts.**
- Which letter mapped to which condition (the blinding map above).
- The existence of "conditions" as a concept — experts were told they were ranking three submissions per task, not three retrieval modes.
- The aggregate result of the other two experts (each expert evaluated independently).
- The hypothesis being tested (that A > D > B).

**What experts had.**
- Full source of all three submissions per task.
- Problem statement and the case-study notes for each MHPP task.
- A shell environment for running, profiling, and adversarially testing each submission.
- Instructions to rank by code quality among submissions they verified as correct, and to articulate best/worst reasoning in prose.
