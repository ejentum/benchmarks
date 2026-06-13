"""
Deterministic oracle for the frame-trap eval. THE SOURCE OF TRUTH.
Agents never see this file. They get SPEC.md only and submit a min_badness().
This oracle grades a submission against a reference DP optimum on a frozen,
deterministic vector set, and reports the frame signal separately:
  - DISCRIMINATING vectors: greedy(wrong frame) > optimum. Passing these REQUIRES
    the global-optimization frame. This is the measurement.
  - BASIC vectors: greedy == optimum. Passing these only needs basic correctness.
  - EDGE vectors: single word, all-fit, overflow word, etc.
No LLM anywhere. Run:  python oracle.py            -> self-validates the trap
                       python oracle.py <subfile>  -> grades one submission
"""
import importlib.util, os, random, sys

def _used(lengths, i, j):
    return sum(lengths[i:j]) + (j - i - 1)

def _line_ok(lengths, i, j, width):
    n_words = j - i
    if _used(lengths, i, j) <= width:
        return True
    return n_words == 1 and lengths[i] > width  # lone overlong word may overflow

def _line_badness(lengths, i, j, width, is_last):
    if is_last:
        return 0
    trailing = width - _used(lengths, i, j)
    if trailing < 0:
        trailing = 0
    return trailing ** 3

def dp_min(lengths, width):
    """Reference optimum: minimum total badness over all valid line breakings."""
    n = len(lengths)
    INF = float("inf")
    dp = [INF] * (n + 1)
    dp[n] = 0
    for i in range(n - 1, -1, -1):
        j = i + 1
        while j <= n:
            if not _line_ok(lengths, i, j, width):
                if j == i + 1:      # lone word is always placeable (fits or overflows)
                    j += 1
                    continue
                break
            cand = _line_badness(lengths, i, j, width, is_last=(j == n)) + dp[j]
            if cand < dp[i]:
                dp[i] = cand
            j += 1
    return dp[0]

def greedy(lengths, width):
    """The WRONG frame: pack max words per line. Used only to validate the trap."""
    n = len(lengths)
    lines, i = [], 0
    while i < n:
        j = i + 1
        while j < n and _line_ok(lengths, i, j + 1, width):
            j += 1
        lines.append((i, j))
        i = j
    return sum(_line_badness(lengths, i, j, width, is_last=(k == len(lines) - 1))
               for k, (i, j) in enumerate(lines))

def _build_vectors():
    """Deterministic curated set. (lengths, width, expected_optimum, category)."""
    rng = random.Random(20260613)
    disc, basic = [], []
    while len(disc) < 30 or len(basic) < 18:
        n = rng.randint(5, 16)
        width = rng.randint(8, 22)
        lengths = [rng.randint(1, min(width + 2, 12)) for _ in range(n)]
        d, g = dp_min(lengths, width), greedy(lengths, width)
        if d == float("inf"):
            continue
        if g > d and len(disc) < 30:
            disc.append((lengths, width, d, "disc"))
        elif g == d and len(basic) < 18:
            basic.append((lengths, width, d, "basic"))
    edges = []
    def add_edge(lengths, width):
        edges.append((lengths, width, dp_min(lengths, width), "edge"))
    add_edge([3], 10)                       # single word
    add_edge([2, 2, 2], 20)                 # all fit on one line
    add_edge([15, 2, 3], 10)                # leading overlong word overflows
    add_edge([2, 3, 15, 4], 10)             # interior overlong word
    add_edge([5, 5], 11)                    # two words, fit
    add_edge([9, 9, 9, 9], 9)               # each word its own line
    add_edge([1, 1, 1, 1, 1, 1], 3)         # many tiny words
    return disc + basic + edges

VECTORS = _build_vectors()

def grade(submission_path):
    spec = importlib.util.spec_from_file_location("sub", submission_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    fn = getattr(mod, "min_badness")
    cats = {"disc": [0, 0], "basic": [0, 0], "edge": [0, 0]}
    fails = []
    for lengths, width, expected, cat in VECTORS:
        words = ["x" * L for L in lengths]
        cats[cat][1] += 1
        try:
            got = fn(words, width)
        except Exception as e:
            got = f"EXC:{e}"
        if got == expected:
            cats[cat][0] += 1
        else:
            fails.append((cat, lengths, width, expected, got))
    return cats, fails

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # self-validate: dp passes everything; greedy must FAIL the discriminating set
        disc = [v for v in VECTORS if v[3] == "disc"]
        gfail = sum(1 for lengths, width, exp, _ in disc if greedy(lengths, width) != exp)
        print(f"vectors: {len(VECTORS)} (disc={sum(1 for v in VECTORS if v[3]=='disc')}, "
              f"basic={sum(1 for v in VECTORS if v[3]=='basic')}, "
              f"edge={sum(1 for v in VECTORS if v[3]=='edge')})")
        print(f"greedy fails {gfail}/{len(disc)} discriminating vectors  "
              f"(frame trap is {'LIVE' if gfail == len(disc) else 'WEAK'})")
        print("reference dp_min is internally consistent (expected answers frozen from it).")
    else:
        cats, fails = grade(sys.argv[1])
        for c in ("disc", "basic", "edge"):
            print(f"{c:5}: {cats[c][0]}/{cats[c][1]}")
        print(f"FAILURES: {len(fails)}")
        for cat, lengths, width, exp, got in fails[:8]:
            print(f"  [{cat}] W={width} lens={lengths} exp={exp} got={got}")
