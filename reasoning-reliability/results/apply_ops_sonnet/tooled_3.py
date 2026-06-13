"""Single-pass text rewrite per SPEC2.md.

apply_ops scans the ORIGINAL text once, left to right. At each cursor position
the first op (in list order) whose `find` is an exact prefix at that position
fires: its `replace` is appended to the output and the cursor jumps past the
matched span in the original text. Text emitted by a `replace` is output only;
it is never re-scanned. Op priority is list order, not longest-match.
"""

from typing import List, Tuple


def apply_ops(text: str, ops: List[Tuple[str, str]]) -> str:
    out: List[str] = []
    i = 0
    n = len(text)
    while i < n:
        fired = False
        # List order, NOT longest-match: the first op whose `find` matches wins.
        for find, replace in ops:
            flen = len(find)
            # Match against the ORIGINAL text starting at the cursor.
            # `find` is guaranteed non-empty by the contract.
            if text[i:i + flen] == find:
                out.append(replace)          # emitted text is output-only
                i += flen                    # advance past the matched span
                fired = True
                break
        if not fired:
            # No op matched here: copy one original character verbatim.
            out.append(text[i])
            i += 1
    return "".join(out)


if __name__ == "__main__":
    assert apply_ops("a", [("a", "b"), ("b", "c")]) == "b"
    assert apply_ops("ab", [("a", "x"), ("ab", "y")]) == "xb"
    assert apply_ops("cat", [("cat", "dog"), ("dog", "bird")]) == "dog"
    assert apply_ops("hello", []) == "hello"
    # Empty replacement deletes the matched span.
    assert apply_ops("aXb", [("X", "")]) == "ab"
    # `find` longer than the remaining text never matches.
    assert apply_ops("a", [("ab", "z")]) == "a"
    print("all checks passed")
