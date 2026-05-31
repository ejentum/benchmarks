# Changelog

## 2026-05-31: HLE-15 ablation added

Round 2 of the Ejentum harness benchmark series added to `hle-15/`. Claude Opus 4.8 on 15 text-only multiple-choice questions from Humanity's Last Exam, three conditions (B raw, D dynamic reasoning, A adaptive reasoning), 45 solve agents, pre-registered before dispatch.

### Findings

- Pass rates: B=4/15, D=4/15, A=2/15
- Observed ordering is B = D > A. The pre-registered prediction (A > D > B) was not validated on this benchmark; the adaptive arm regressed two raw passes below the bare model
- The three arms collapse to identical per-category scores in 7 of 8 categories. Math is the only category that differentiated: A scored 2/3, B and D each 1/3
- Round 1 ([MHPP-10](mhpp-10/)) saturated at 9/9/9 and the A > D > B ordering was visible only in blind expert qualitative review. Round 2 tested the opposite regime (non-saturated, frontier) and pass-rate spread emerged in the wrong direction

### Methodological notes

- Pre-registration committed before any solver ran (see PRE_REGISTRATION.md in dedicated repo `ejentum/ablation-hle-15`)
- 15 questions stratified across 8 HLE categories for breadth
- Multiple-choice subset used for trivial exact-letter scoring (no judge agent needed)
- Tested the flagship reasoning + adaptive-reasoning modes (311-ability pool), distinct from Round 1's code modes (128 abilities)

---

## 2026-05-31: MHPP-10 ablation added

Round 1 of the Ejentum harness benchmark series added to `mhpp-10/`. Claude Opus 4.8 on the 10 hardest MHPP tasks, three conditions (B raw, D dynamic code, A adaptive code), 30 solve agents, pre-registered before dispatch, blind expert review by 3 independent SWE personas with X/Y/Z letter rotation across tasks.

### Findings

- Pass rate saturated: 9/10 across all three conditions (10/10 after correcting one AI-authored test bug)
- Blind expert review: A 26/27, D 19/27, B 9/27 (last on every ballot). 8 of 9 ballots produced exactly A > D > B
- Code character differs systematically across conditions even when pass rate does not: +240% comments, +100% defensive guards, +26% LOC for A vs B
- One reviewer measured a 21,000x speedup on adversarial input (5000 chars, count=5000) on A's sliding-window solution vs D's brute force

### Methodological notes

- Pre-registration committed before any solver ran (SHA 851f37e5 in dedicated repo `ejentum/ablation-mhpp-10`)
- AI-authored test cases used because MHPP withholds canonicals; one test (mhpp_130) was identified post hoc as miscalibrated and corrected in REPORT.md
- The dedicated repo `ejentum/ablation-mhpp-10` is the canonical artifact with full per-agent transcripts; this subdir is the indexed entry in the benchmark series

---

## 2026-04-17: Terminology migration

Public-facing terminology was standardized across the Ejentum ecosystem to reflect the four-product architecture introduced in April 2026. This change is narrative-only: no benchmark numbers, methodology, or scientific claims are affected.

### What changed

| Before | After | Reason |
|--------|-------|--------|
| `scaffold` | `injection` (the mechanism) / `ability` (the object) / `harness` (the product) | Aligns with the four-product positioning: Reasoning Harness, Code Harness, Anti-Deception Harness, Memory Harness |
| API mode `"single"` | API mode `"reasoning"` | Mode names now match the product layer. The old `"single"` was reasoning-only. |
| API mode `"multi"` | API mode `"reasoning-multi"` | Mode names now match the product layer. |
| `Ki` (as mode name) | `reasoning` | `Ki` is retained as a plan tier name on [ejentum.com/pricing](https://ejentum.com/pricing) but no longer used as a mode identifier. |
| `Haki` (as mode name) | `reasoning-multi` | Same as above. |

### Current API modes

The Logic API now exposes seven modes across four product layers:

| Mode | Product Layer | Abilities |
|------|---------------|-----------|
| `reasoning` | Reasoning Harness | 311 |
| `reasoning-multi` | Reasoning Harness | 311 (primary + cross-domain guards) |
| `code` | Code Harness | 128 |
| `code-multi` | Code Harness | 128 (primary + cross-domain guards) |
| `anti-deception` | Anti-Deception Harness | 139 |
| `memory` | Memory Harness | 101 |
| `memory-multi` | Memory Harness | 101 (primary + cross-domain guards) |

### What was updated

- All benchmark README files (arc-agi-3, bbh-causalbench-musr, ejbench, lcb-hard, elephant, coding-benchmark)
- All published reports (REPORT.md, SCIENTIFIC_REPORT.md across all benchmarks)
- All Python benchmark runner scripts
- Cross-references and links to ejentum.com documentation

### What was preserved

- **Raw JSON benchmark artifacts** (generations, judgments, results) retain their original field names and mode values (`"mode": "single"`, `scaffold_length`, etc.). These files capture what was actually tested at the time of each run and are preserved as scientific record. If you re-run any benchmark today using the current runner scripts, the output will use current terminology.
- **Research paper** ("Under Pressure: RA²R and the Emergence of Uninstructed Reasoning Behaviors in Scaffold-Augmented Language Models") retains its original title on Zenodo, SSRN, and ORCID. the paper is a published artifact and cannot be retroactively renamed.
- **"Cognitive Scaffolding Thesis"** is a proper noun (the name of the published thesis) and remains unchanged.

### Where to learn more

- [Product documentation](https://ejentum.com/docs)
- [Unified skill file](https://ejentum.com/docs/skill_unified). teaches agents to autonomously route across all four harnesses
- [Current API reference](https://ejentum.com/docs/api_reference)
