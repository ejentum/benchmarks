# MHPP-10 Ablation

Code Harness benchmark. 10 hardest MHPP tasks, Claude Opus 4.8, three conditions: B (raw), D (dynamic code), A (adaptive code). Pre-registered ladder A > D > B before any solver ran.

## Headline

| | Pass rate | Blind expert review (max 27) |
|---|---|---|
| **B (raw)** | 9/10 | **9** |
| **D (dynamic code)** | 9/10 | **19** |
| **A (adaptive code)** | 9/10 | **26** |

Pass rate saturated on Opus 4.8 (10/10 corrected for one buggy AI-authored test). Blind expert review by 3 independent SWE personas converged on A > D > B in 8 of 9 ballots. One reviewer ran adversarial inputs at scale and measured a 21,000x speedup on A's solution vs D's for the substring-counting task (5000 chars, count=5000: 21.4s for brute force, 0.001s for sliding window).

## Findings

- The harness operates on code character even when pass rate is saturated: +240% comments, +100% defensive guards, +26% LOC.
- A consistently picked better algorithmic class (sliding window over brute force; backward DP over forward DP; closed form over iteration).
- B was last on every blind-review ballot (9/9 unanimous on lowest rank).
- The single failed task (mhpp_130) was a test-authoring error in the AI-generated test suite; all three solutions were correct. Corrected pass rate: 10/10/10.

## Dedicated repo

The canonical artifact, with full per-agent transcripts and the workflow scripts that orchestrated the 30-agent ablation + 3-agent blind eval, lives at: **https://github.com/ejentum/ablation-mhpp-10**

## Files in this directory

| File | Purpose |
|---|---|
| `PRE_REGISTRATION.md` | Predictions committed before any solver ran (SHA 851f37e5 in dedicated repo) |
| `RESULTS.md` | Pass-rate scoreboard |
| `REPORT.md` | Full scientific writeup with methods, threats to validity, follow-ups |
| `case_studies.md` | Line-by-line reading of three case-study tasks (mhpp_130, 132, 136) |
| `BLIND_EVAL.md` | Three blind SWE-expert reviewers, full reasoning un-blinded |
| `raw_scores.json` | Per-(task, condition) execution results |
| `chart.svg` | Three-bar pass-rate chart |
| `workflow.js` | The Claude Code workflow script that orchestrated the 30 solve agents |

## Reproducibility

The workflow script (`workflow.js`) is dispatchable via Claude Code's Workflow tool. It pulls MHPP from HuggingFace at runtime, authors test cases, dispatches 30 solve agents in parallel batches of 16, scores them in subprocess, and commits results back to a fresh GitHub repo. The blind evaluation runs as a separate workflow (see dedicated repo).

## Status

Round 1 of a benchmark series. Round 2 in progress (Humanity's Last Exam, 15 questions, reasoning + adaptive-reasoning modes).
