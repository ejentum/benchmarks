"""apply_ops: single-pass, original-text cursor-based string rewriting.

Semantics (per SPEC2.md), the parts that make off-the-shelf tools wrong:
  * Matching is ALWAYS against the original `text` at the current cursor.
  * At a position, ops are tried in LIST ORDER; the first whose `find` matches
    fires. This is *not* longest-match.
  * A fired op emits its `replace` to the output and advances the cursor by
    len(find). Emitted text is output only and is NEVER re-scanned.
  * If no op matches, emit the single original char and advance by 1.

This is a cursor + output-buffer string simulation, not regex / str.replace.
"""

from typing import List, Tuple


def apply_ops(text: str, ops: List[Tuple[str, str]]) -> str:
    out: List[str] = []
    i = 0
    n = len(text)

    while i < n:
        for find, replace in ops:
            flen = len(find)
            # find is guaranteed non-empty; match against the ORIGINAL text.
            if text[i:i + flen] == find:
                out.append(replace)
                i += flen
                break
        else:
            # No op matched at this position: copy one original character.
            out.append(text[i])
            i += 1

    return "".join(out)


if __name__ == "__main__":
    assert apply_ops("a", [("a", "b"), ("b", "c")]) == "b"
    assert apply_ops("ab", [("a", "x"), ("ab", "y")]) == "xb"
    assert apply_ops("cat", [("cat", "dog"), ("dog", "bird")]) == "dog"
    assert apply_ops("hello", []) == "hello"
    # replace may be empty:
    assert apply_ops("aXb", [("X", "")]) == "ab"
    # no re-scan: emitted text never re-triggers a match
    assert apply_ops("a", [("a", "aa"), ("aa", "z")]) == "aa"
    print("ok")
