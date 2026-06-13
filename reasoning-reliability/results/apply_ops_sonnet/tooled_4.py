"""apply_ops: deterministic single-pass string rewriter.

Semantics (per spec):
  - Scan the ORIGINAL text once, left to right, with a cursor starting at 0.
  - At each position, the first op (in list order) whose `find` matches the
    original text starting at the cursor fires: emit its `replace`, advance the
    cursor by len(find).
  - If no op matches, emit the single original character and advance by 1.
  - Emitted `replace` text is output only; it is never re-scanned.
  - Priority at a position is list order, NOT longest match.
"""


def apply_ops(text: str, ops: list[tuple[str, str]]) -> str:
    out = []
    i = 0
    n = len(text)
    while i < n:
        for find, replace in ops:
            # find is guaranteed non-empty; match against the ORIGINAL text.
            if text[i:i + len(find)] == find:
                out.append(replace)
                i += len(find)
                break
        else:
            # No op matched at this position: emit one original char.
            out.append(text[i])
            i += 1
    return "".join(out)


if __name__ == "__main__":
    assert apply_ops("a", [("a", "b"), ("b", "c")]) == "b"
    assert apply_ops("ab", [("a", "x"), ("ab", "y")]) == "xb"
    assert apply_ops("cat", [("cat", "dog"), ("dog", "bird")]) == "dog"
    assert apply_ops("hello", []) == "hello"
    print("ok")
