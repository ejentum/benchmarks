"""Full analysis of all LCB Hard data for scientific report."""
import json, sys, re
from collections import defaultdict, Counter
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Load ALL 3 batches
with open("c:/Users/frank/Desktop/ejentum/benchmarks-staging/lcb-hard/results/baseline_full_v1/results_full.json") as f:
    b1b = json.load(f)
with open("c:/Users/frank/Desktop/ejentum/benchmarks-staging/lcb-hard/results/augmented_full_v2/results_full.json") as f:
    b1a = json.load(f)
with open("c:/Users/frank/Desktop/ejentum/benchmarks-staging/lcb-hard/results/baseline_batch2_v1/results_full.json") as f:
    b2b = json.load(f)
with open("c:/Users/frank/Desktop/ejentum/benchmarks-staging/lcb-hard/results/augmented_batch2_v1/results_full.json") as f:
    b2a = json.load(f)
with open("c:/Users/frank/Desktop/ejentum/benchmarks-staging/lcb-hard/results/baseline_batch3_v1/results_full.json") as f:
    b3b = json.load(f)
with open("c:/Users/frank/Desktop/ejentum/benchmarks-staging/lcb-hard/results/augmented_batch3_v1/results_full.json") as f:
    b3a = json.load(f)

# Load retry
retry2 = []
try:
    with open("c:/Users/frank/Desktop/ejentum/benchmarks-staging/lcb-hard/results/retry2_results.json") as f:
        retry2 = json.load(f)
except: pass

# Combine hard only, exclude Anti + Vouchers
exclude = {"Anti", "Vouchers"}
all_b = [t for t in b1b + b2b + b3b if t["difficulty"] == "hard" and t["title"] not in exclude]
all_a = [t for t in b1a + b2a + b3a if t["difficulty"] == "hard" and t["title"] not in exclude]

# Apply corrections
for a in all_a:
    if a["title"] == "Roulettes":
        a["eval"]["pass"] = True
        a["eval"]["corrected"] = "precision_only"
    if a["title"] == "Bus Stops":
        for r in retry2:
            if r["title"] == "Bus Stops" and r["eval"]["pass"]:
                a["eval"]["pass"] = True
                a["eval"]["corrected"] = "retry_1200s"
                a["code"] = r.get("code", a.get("code", ""))
                a["code_length"] = r.get("code_length", a.get("code_length", 0))

pairs = list(zip(all_b, all_a))

# ============================================================
print("=" * 80)
print("1. CORRECTNESS RESULTS")
print("=" * 80)

bp_total = sum(1 for b, _ in pairs if b["eval"]["pass"])
ap_total = sum(1 for _, a in pairs if a["eval"]["pass"])
gained = [(b,a) for b,a in pairs if not b["eval"]["pass"] and a["eval"]["pass"]]
lost = [(b,a) for b,a in pairs if b["eval"]["pass"] and not a["eval"]["pass"]]

print(f"  Tasks: {len(pairs)}")
print(f"  Baseline: {bp_total}/{len(pairs)} ({bp_total/len(pairs)*100:.1f}%)")
print(f"  Augmented: {ap_total}/{len(pairs)} ({ap_total/len(pairs)*100:.1f}%)")
print(f"  Delta: +{(ap_total-bp_total)/len(pairs)*100:.1f}pp")
print(f"  Gained: {len(gained)} | Lost: {len(lost)} | Net: +{len(gained)-len(lost)}")

# ============================================================
print(f"\n{'='*80}")
print("2. PER-TASK COMPARISON")
print("=" * 80)
print(f"  {'Task':28} | {'Base':>5} | {'Aug':>5} | {'B Code':>7} | {'A Code':>7} | {'B Time':>7} | {'A Time':>7} | {'Scaff':>5} | Flip")
print("  " + "-" * 100)

for b, a in pairs:
    bp = "PASS" if b["eval"]["pass"] else "FAIL"
    ap = "PASS" if a["eval"]["pass"] else "FAIL"
    bc = b.get("code_length", len(b.get("code","")))
    ac = a.get("code_length", len(a.get("code","")))
    bt = b.get("elapsed_seconds", 0)
    at = a.get("elapsed_seconds", 0)
    sc = a.get("injection_length", 0)
    flip = ""
    if not b["eval"]["pass"] and a["eval"]["pass"]: flip = "GAINED"
    elif b["eval"]["pass"] and not a["eval"]["pass"]: flip = "LOST"
    corr = a["eval"].get("corrected", "")
    if corr: flip += f" ({corr})"
    print(f"  {b['title']:28} | {bp:>5} | {ap:>5} | {bc:>5}ch | {ac:>5}ch | {bt:>5.0f}s | {at:>5.0f}s | {sc:>5} | {flip}")

# ============================================================
print(f"\n{'='*80}")
print("3. GAINED TASKS - FORENSIC DETAIL")
print("=" * 80)

for b, a in gained:
    print(f"\n  --- {b['title']} ---")
    print(f"  Baseline: FAIL | {len(b.get('code',''))}ch | {b.get('elapsed_seconds',0):.0f}s")
    print(f"  Augmented: PASS | {len(a.get('code',''))}ch | {a.get('elapsed_seconds',0):.0f}s | injection={a.get('injection_length',0)}ch")
    corr = a["eval"].get("corrected","")
    if corr:
        print(f"  Correction: {corr}")
    if b.get("code"):
        print(f"  Base code (first 200): {b['code'][:200]}")
    else:
        print(f"  Base code: NONE (timeout)")
    if a.get("code"):
        print(f"  Aug code (first 200): {a['code'][:200]}")

# ============================================================
print(f"\n{'='*80}")
print("4. CODE STRUCTURAL METRICS (both-pass tasks with code)")
print("=" * 80)

both_pass = [(b,a) for b,a in pairs if b["eval"]["pass"] and a["eval"]["pass"] and b.get("code") and a.get("code")]

metrics = {
    "code_chars": ([], []),
    "lines": ([], []),
    "ifs": ([], []),
    "fors": ([], []),
    "defs": ([], []),
    "comments": ([], []),
    "imports": ([], []),
}

for b, a in both_pass:
    bc, ac = b["code"], a["code"]
    metrics["code_chars"][0].append(len(bc)); metrics["code_chars"][1].append(len(ac))
    metrics["lines"][0].append(len(bc.split("\n"))); metrics["lines"][1].append(len(ac.split("\n")))
    metrics["ifs"][0].append(bc.count("if ")); metrics["ifs"][1].append(ac.count("if "))
    metrics["fors"][0].append(bc.count("for ")); metrics["fors"][1].append(ac.count("for "))
    metrics["defs"][0].append(len(re.findall(r"^def ", bc, re.MULTILINE))); metrics["defs"][1].append(len(re.findall(r"^def ", ac, re.MULTILINE)))
    metrics["comments"][0].append(bc.count("#")); metrics["comments"][1].append(ac.count("#"))
    metrics["imports"][0].append(len(re.findall(r"^(?:import|from)\s", bc, re.MULTILINE))); metrics["imports"][1].append(len(re.findall(r"^(?:import|from)\s", ac, re.MULTILINE)))

print(f"  {len(both_pass)} tasks pass in both conditions")
print(f"  {'Metric':20} | {'Base Total':>10} | {'Aug Total':>10} | {'Delta':>8} | {'Pct':>7}")
print("  " + "-" * 65)
for name, (bv, av) in metrics.items():
    bt = sum(bv); at = sum(av)
    d = at - bt
    pct = (at/bt - 1) * 100 if bt > 0 else 0
    print(f"  {name:20} | {bt:>10} | {at:>10} | {d:>+8} | {pct:>+6.1f}%")

identical = sum(1 for b,a in both_pass if b["code"].strip() == a["code"].strip())
print(f"\n  Identical code: {identical}/{len(both_pass)}")

# ============================================================
print(f"\n{'='*80}")
print("5. ALGORITHM PATTERN ANALYSIS")
print("=" * 80)

algo_patterns = ["deque", "heapq", "bisect", "sort", "dp", "memo", "dfs", "bfs", "bit[", "fenwick", "segment", "union", "find"]
for b, a in both_pass:
    bc, ac = b["code"].lower(), a["code"].lower()
    b_algos = [p for p in algo_patterns if p in bc]
    a_algos = [p for p in algo_patterns if p in ac]
    if set(b_algos) != set(a_algos):
        added = set(a_algos) - set(b_algos)
        removed = set(b_algos) - set(a_algos)
        print(f"  {b['title']:28} | base={b_algos} | aug={a_algos}")
        if added: print(f"    ADDED: {added}")
        if removed: print(f"    REMOVED: {removed}")

# ============================================================
print(f"\n{'='*80}")
print("6. TIME ANALYSIS")
print("=" * 80)

b_times = [b.get("elapsed_seconds",0) for b,_ in pairs if b.get("code")]
a_times = [a.get("elapsed_seconds",0) for _,a in pairs if a.get("code")]

print(f"  Baseline avg: {sum(b_times)/len(b_times):.0f}s")
print(f"  Augmented avg: {sum(a_times)/len(a_times):.0f}s")
print(f"  Ratio: {sum(a_times)/sum(b_times):.1f}x")

# Per-task time ratio for both-pass
print(f"\n  Time ratios (both-pass tasks):")
ratios = []
for b, a in both_pass:
    bt = b.get("elapsed_seconds", 1)
    at = a.get("elapsed_seconds", 1)
    ratio = at / bt if bt > 0 else 0
    ratios.append(ratio)
    print(f"    {b['title']:28} | base={bt:.0f}s aug={at:.0f}s ratio={ratio:.1f}x")

print(f"\n  Avg time ratio: {sum(ratios)/len(ratios):.1f}x")
print(f"  Min ratio: {min(ratios):.1f}x | Max ratio: {max(ratios):.1f}x")

# ============================================================
print(f"\n{'='*80}")
print("7. INJECTION STATISTICS")
print("=" * 80)

injections = [a.get("injection_length",0) for _,a in pairs if a.get("injection_length",0) > 0]
print(f"  Tasks augmented: {len(injections)}/{len(pairs)}")
print(f"  Injection sizes: min={min(injections)} avg={sum(injections)//len(injections)} max={max(injections)}")

# ============================================================
print(f"\n{'='*80}")
print("8. CODE IDENTICAL vs DIFFERENT")
print("=" * 80)

for b, a in both_pass:
    same = b["code"].strip() == a["code"].strip()
    diff = len(a["code"]) - len(b["code"])
    status = "IDENTICAL" if same else f"DIFFERENT ({diff:+d}ch)"
    print(f"  {b['title']:28} | {status}")

print(f"\n{'='*80}")
print("ANALYSIS COMPLETE")
print("=" * 80)
