"""apply_ops: single left-to-right pass over the ORIGINAL text.

Semantics (per SPEC2.md), distinct from str.replace / sequential rewriting:

  * One pass over the original input with a cursor starting at 0.
  * At cursor i, ops are tried in LIST ORDER (not longest-match). The first op
    whose `find` satisfies text[i : i+len(find)] == find fires.
  * A firing op appends its `replace` to the output and advances the cursor by
    len(find) over the ORIGINAL text.
  * If no op matches at i, append text[i] and advance by 1.
  * Matching is ALWAYS against the original text. Emitted `replace` text is
    output-only and is never re-scanned, so it can never trigger further matches.
"""


def apply_ops(text: str, ops: list) -> str:
    out = []
    i = 0
    n = len(text)
    while i < n:
        fired = False
        # List order is the priority, NOT longest match.
        for find, replace in ops:
            flen = len(find)
            # find is guaranteed non-empty; match against the ORIGINAL text only.
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
    print("all assertions passed")
