"""Generate TypeScript data for 10 LCB task profiles."""
import json, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

with open("results/baseline/results_with_code.json") as f:
    base = {t["title"]: t for t in json.load(f)}
with open("results/augmented/results_with_code.json") as f:
    aug = {t["title"]: t for t in json.load(f)}

selected = [
    ("LCB-01", "Best Performances", "Reasoning spiral rescued: 610s of thinking produced zero code. Injection provided convergence structure via BIT/Fenwick tree decomposition."),
    ("LCB-02", "Tangency of Cuboids", "Reasoning spiral rescued: 1190s of thinking produced zero code. Injection structured 3D spatial reasoning for cuboid intersection detection."),
    ("LCB-03", "Art Gallery on Graph", "Premature convergence caught: baseline accepted first-plausible BFS traversal in 11s that failed 2/3 tests. Injection suppression signals forced boundary verification."),
    ("LCB-04", "Roulettes", "Algorithm correct in both conditions. Baseline had floating-point precision mismatch. Injection produced cleaner DP implementation."),
    ("LCB-05", "Defect", "The anomaly: injection made the model FASTER. 515s baseline to 374s augmented. -324 chars, -27% time. Injection helped skip exploratory thinking phase."),
    ("LCB-06", "Sleep Log", "Conciseness: -183 chars. Injection produced tighter implementation of the same bisect-based algorithm."),
    ("LCB-07", "Complete Binary Tree", "Conciseness: -178 chars. Injection helped model find a more direct approach to tree traversal."),
    ("LCB-08", "Cans and Openers", "Algorithm enrichment: augmented added bisect binary search alongside existing sort. More sophisticated data structure choice."),
    ("LCB-09", "MEX", "Different approach: -165 chars. Injection produced a structurally different solution with 50% token overlap (Jaccard 0.500)."),
    ("LCB-10", "Square Permutation", "Most different solution: only 40.5% token overlap. Completely different algorithmic approach, both correct."),
]

def escape_ts(s):
    return s.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")

print("// LiveCodeBench Hard task profiles — auto-generated")
print("// 10 selected tasks from 28 hard AtCoder competitive programming problems")
print()
print("export interface CodeTask {")
print("    id: string;")
print("    title: string;")
print("    platform: string;")
print("    source: string;")
print("    sourceCategory: string;")
print("    difficulty: string;")
print("    narrative: string;")
print("    baselinePass: boolean;")
print("    augmentedPass: boolean;")
print("    flip: string;")
print("    baselineCode: string;")
print("    augmentedCode: string;")
print("    baselineCodeLength: number;")
print("    augmentedCodeLength: number;")
print("    baselineTime: number;")
print("    augmentedTime: number;")
print("    injectionLength: number;")
print("}")
print()
print("export const codeTasks: CodeTask[] = [")

for task_id, title, narrative in selected:
    b = base[title]
    a = aug[title]
    bp = b["eval"]["pass"]
    ap = a["eval"]["pass"]
    flip = "GAINED" if not bp and ap else ""
    b_code = escape_ts(b.get("code", "") or "// No code produced (timeout)")
    a_code = escape_ts(a.get("code", "") or "// No code produced (timeout)")

    print(f"    {{")
    print(f"        id: '{task_id}',")
    print(f"        title: '{title}',")
    print(f"        platform: 'AtCoder',")
    print(f"        source: 'LiveCodeBench',")
    print(f"        sourceCategory: 'LiveCodeBench Hard',")
    print(f"        difficulty: 'hard',")
    print(f"        narrative: `{escape_ts(narrative)}`,")
    print(f"        baselinePass: {'true' if bp else 'false'},")
    print(f"        augmentedPass: {'true' if ap else 'false'},")
    print(f"        flip: '{flip}',")
    print(f"        baselineCode: `{b_code}`,")
    print(f"        augmentedCode: `{a_code}`,")
    print(f"        baselineCodeLength: {b.get('code_length', 0)},")
    print(f"        augmentedCodeLength: {a.get('code_length', 0)},")
    print(f"        baselineTime: {b.get('elapsed_seconds', 0)},")
    print(f"        augmentedTime: {a.get('elapsed_seconds', 0)},")
    print(f"        injectionLength: {a.get('injection_length', 0)},")
    print(f"    }},")

print("];")
