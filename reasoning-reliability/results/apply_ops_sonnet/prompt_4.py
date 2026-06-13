"""apply_ops: single left-to-right pass over the ORIGINAL text.

Semantics (per spec):
- Cursor walks the original `text` from position 0.
- At each position i, ops are considered in their given LIST ORDER; the FIRST op
  whose `find` matches `text[i:i+len(find)]` fires (NOT longest-match).
- A fired op appends its `replace` to output and advances the cursor by
  len(find) over the ORIGINAL text.
- If no op matches at i, the single original char text[i] is appended and the
  cursor advances by 1.
- Matching is ALWAYS against the original text; emitted `replace` text is
  output-only and is never re-scanned.
"""


def apply_ops(text, ops):
    out = []
    i = 0
    n = len(text)
    while i < n:
        fired = False
        # List order = priority. First matching op at position i wins.
        for find, replace in ops:
            flen = len(find)
            # find is guaranteed non-empty; compare against the ORIGINAL text.
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
    # empty replacement deletes the matched span
    assert apply_ops("aXb", [("X", "")]) == "ab"
    # no re-scan: emitted text never matches further
    assert apply_ops("aa", [("a", "aa")]) == "aaaa"
    print("all checks passed")
