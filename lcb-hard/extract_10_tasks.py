"""Extract 10 selected LCB tasks for website task profiles."""
import json, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

with open("results/baseline/results_with_code.json") as f:
    base = {t["title"]: t for t in json.load(f)}
with open("results/augmented/results_with_code.json") as f:
    aug = {t["title"]: t for t in json.load(f)}

selected = [
    "Best Performances",
    "Tangency of Cuboids",
    "Art Gallery on Graph",
    "Roulettes",
    "Defect",
    "Sleep Log",
    "Complete Binary Tree",
    "Cans and Openers",
    "MEX",
    "Square Permutation",
]

for i, title in enumerate(selected):
    b = base[title]
    a = aug[title]
    bp = b["eval"]["pass"]
    ap = a["eval"]["pass"]

    print(f"// LCB-{i+1:02d}: {title}")
    print(f"// Baseline: {'PASS' if bp else 'FAIL'} ({b['code_length']}ch, {b['elapsed_seconds']:.0f}s)")
    print(f"// Augmented: {'PASS' if ap else 'FAIL'} ({a['code_length']}ch, {a['elapsed_seconds']:.0f}s, injection={a.get('injection_length',0)}ch)")
    print(f"// Flip: {'GAINED' if not bp and ap else 'both pass'}")
    print()
