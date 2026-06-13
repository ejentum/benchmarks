def apply_ops(text, ops):
    """Apply ordered (find, replace) ops in a single left-to-right pass over the
    ORIGINAL text.

    Semantics (per spec):
      - Cursor starts at 0 and scans the original `text` only.
      - At each position i, consider ops in their given LIST ORDER. The first op
        whose `find` exactly matches `text[i:i+len(find)]` fires (NOT longest-match).
      - On a fire: append `replace` to output, advance cursor by len(find).
      - On no match: append the single original char text[i], advance cursor by 1.
      - Emitted replacement text is output-only and is NEVER re-scanned.
    """
    out = []
    i = 0
    n = len(text)
    while i < n:
        fired = False
        for find, replace in ops:
            flen = len(find)
            # find is guaranteed non-empty; exact match against ORIGINAL text.
            if text[i:i + flen] == find:
                out.append(replace)
                i += flen
                fired = True
                break  # list-order priority: first match wins
        if not fired:
            out.append(text[i])
            i += 1
    return "".join(out)


if __name__ == '__main__':
    assert apply_ops("a", [("a", "b"), ("b", "c")]) == "b"
    assert apply_ops("ab", [("a", "x"), ("ab", "y")]) == "xb"
    assert apply_ops("cat", [("cat", "dog"), ("dog", "bird")]) == "dog"
    assert apply_ops("hello", []) == "hello"
    # empty replace
    assert apply_ops("abc", [("b", "")]) == "ac"
    # no re-scan of emitted text
    assert apply_ops("a", [("a", "aa"), ("aa", "z")]) == "aa"
    print("all ok")
