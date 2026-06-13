"""apply_ops: single left-to-right pass text replacement over the ORIGINAL input.

Semantics (per spec):
  - Cursor starts at 0 and scans the original `text` left to right.
  - At each position, ops are tried in list order; the FIRST op whose `find`
    exactly matches the original text at the cursor fires (list-order priority,
    NOT longest match).
  - On a match: append `replace` to the output and advance the cursor by
    len(find).
  - On no match: append the single original character and advance by 1.
  - Matching is always against the original text; emitted replacement text is
    output-only and is never re-scanned.
"""

from typing import List, Tuple


def apply_ops(text: str, ops: List[Tuple[str, str]]) -> str:
    out = []           # collected output fragments (replacements + passthrough chars)
    i = 0              # cursor into the ORIGINAL text
    n = len(text)

    while i < n:
        fired = False
        for find, replace in ops:
            flen = len(find)
            # `find` is guaranteed non-empty per spec; the slice comparison
            # naturally fails past the end of `text`, so no bounds guard needed.
            if text[i:i + flen] == find:
                out.append(replace)
                i += flen
                fired = True
                break
        if not fired:
            out.append(text[i])
            i += 1

    return "".join(out)


if __name__ == '__main__':
    assert apply_ops("a", [("a", "b"), ("b", "c")]) == "b"
    assert apply_ops("ab", [("a", "x"), ("ab", "y")]) == "xb"
    assert apply_ops("cat", [("cat", "dog"), ("dog", "bird")]) == "dog"
    assert apply_ops("hello", []) == "hello"
    # empty replacement
    assert apply_ops("aXbXc", [("X", "")]) == "abc"
    # overlapping handled by advancing past matched span
    assert apply_ops("aaa", [("aa", "b")]) == "ba"
    print("all checks passed")
