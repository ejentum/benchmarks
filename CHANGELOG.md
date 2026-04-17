# Changelog

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
