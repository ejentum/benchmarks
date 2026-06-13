"""
Oracle for the INTERPRETATION-trap eval. THE SOURCE OF TRUTH.
Intended reading: single left-to-right pass over the ORIGINAL text, list-order
op priority, emitted text is never re-scanned. The OBVIOUS wrong reading is the
sequential `for f,r in ops: text = text.replace(f,r)` loop (cascades across the
whole string). A second wrong reading is single-pass but longest-match priority.
Agents never see this file. They get SPEC2.md and submit apply_ops().
Run:  python oracle2.py            -> self-validates that wrong readings fail
      python oracle2.py <subfile>  -> grades one submission
"""
import importlib.util, sys

# ---- reference: the intended single-pass, list-order, no-rescan semantics ----
def apply_ops_ref(text, ops):
    out, i, n = [], 0, len(text)
    while i < n:
        hit = False
        for f, r in ops:
            if f and text.startswith(f, i):
                out.append(r); i += len(f); hit = True; break
        if not hit:
            out.append(text[i]); i += 1
    return "".join(out)

# ---- wrong reading A: sequential global replace (the tempting default) ----
def wrong_sequential(text, ops):
    for f, r in ops:
        text = text.replace(f, r)
    return text

# ---- wrong reading B: single pass but LONGEST match wins (not list order) ----
def wrong_longest(text, ops):
    out, i, n = [], 0, len(text)
    while i < n:
        best = None
        for f, r in ops:
            if f and text.startswith(f, i) and (best is None or len(f) > len(best[0])):
                best = (f, r)
        if best:
            out.append(best[1]); i += len(best[0])
        else:
            out.append(text[i]); i += 1
    return "".join(out)

# (text, ops, category)
RAW_VECTORS = [
    # cascade: sequential re-scans emitted text -> wrong. single-pass -> right.
    ("a", [("a","b"),("b","c")], "cascade"),
    ("cat", [("cat","dog"),("dog","bird")], "cascade"),
    ("xx", [("x","xy"),("y","z")], "cascade"),
    ("ab", [("a","b"),("b","a")], "cascade"),            # swap; sequential collapses both to 'a'
    ("hello", [("h","j"),("j","k")], "cascade"),
    ("12", [("1","2"),("2","3")], "cascade"),
    ("ba", [("b","a"),("a","b")], "cascade"),
    ("aXbX", [("X","Y"),("Y","Z")], "cascade"),
    ("dododo", [("do","re"),("re","mi")], "cascade"),
    ("ne", [("n","ne"),("e","x")], "cascade"),           # sequential: 'n'->'ne' then 'e'->'x' => 'nxx'? check
    # priority: list order beats longest-match.
    ("ab", [("a","x"),("ab","y")], "priority"),
    ("abc", [("a","1"),("abc","9")], "priority"),
    ("foobar", [("foo","X"),("foobar","Z")], "priority"),
    ("aa", [("a","p"),("aa","q")], "priority"),
    # basic: all readings agree (disjoint, no cascade, no overlap).
    ("hello world", [("world","there")], "basic"),
    ("aaa", [("b","c")], "basic"),
    ("abcabc", [("abc","X")], "basic"),
    ("the cat sat", [("cat","dog"),("sat","ran")], "basic"),
    ("mississippi", [("ss","S")], "basic"),
    ("one two three", [("two","2")], "basic"),
    # edge
    ("", [("a","b")], "edge"),
    ("abc", [], "edge"),
    ("aaa", [("a","")], "edge"),                          # delete
    ("ab", [("ab","")], "edge"),
    ("xax", [("a","aa")], "edge"),
]

def _expand():
    out = []
    for text, ops, cat in RAW_VECTORS:
        out.append((text, ops, apply_ops_ref(text, ops), cat))
    return out

VECTORS = _expand()

def grade(submission_path):
    spec = importlib.util.spec_from_file_location("sub2", submission_path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    fn = getattr(mod, "apply_ops")
    cats = {"cascade":[0,0], "priority":[0,0], "basic":[0,0], "edge":[0,0]}
    fails = []
    for text, ops, expected, cat in VECTORS:
        cats[cat][1] += 1
        try: got = fn(text, list(ops))
        except Exception as e: got = f"EXC:{e}"
        if got == expected: cats[cat][0] += 1
        else: fails.append((cat, text, ops, expected, got))
    return cats, fails

if __name__ == "__main__":
    if len(sys.argv) == 1:
        casc = [v for v in VECTORS if v[3]=="cascade"]
        prio = [v for v in VECTORS if v[3]=="priority"]
        sf = sum(1 for t,o,e,c in casc if wrong_sequential(t,o)!=e)
        lf = sum(1 for t,o,e,c in prio if wrong_longest(t,o)!=e)
        sf_basic = sum(1 for t,o,e,c in VECTORS if c in ("basic","edge") and wrong_sequential(t,o)!=e)
        print(f"vectors: {len(VECTORS)} (cascade={len(casc)}, priority={len(prio)}, "
              f"basic={sum(1 for v in VECTORS if v[3]=='basic')}, edge={sum(1 for v in VECTORS if v[3]=='edge')})")
        print(f"WRONG sequential fails {sf}/{len(casc)} cascade vectors  "
              f"(and {sf_basic} of basic+edge -> should be ~0)")
        print(f"WRONG longest-match fails {lf}/{len(prio)} priority vectors")
        print("trap is LIVE" if sf==len(casc) and lf==len(prio) else "trap WEAK -- revise")
    else:
        cats, fails = grade(sys.argv[1])
        for c in ("cascade","priority","basic","edge"):
            print(f"{c:9}: {cats[c][0]}/{cats[c][1]}")
        print(f"FAILURES: {len(fails)}")
        for cat,t,o,e,g in fails[:8]:
            print(f"  [{cat}] text={t!r} ops={o} exp={e!r} got={g!r}")
