def apply_ops(text, ops):
    """Apply ordered (find, replace) ops in a single left-to-right pass over the
    ORIGINAL text.

    Semantics (per spec):
      * Single pass over the original input with a cursor starting at 0.
      * At each cursor position i, ops are considered in their given LIST ORDER.
        The FIRST op whose find exactly matches text[i:i+len(find)] fires
        (list-order priority, NOT longest-match).
      * On a fire: append replace to output, advance cursor by len(find).
      * On no match: append text[i], advance by 1.
      * Matching is ALWAYS against the original text; emitted replace text is
        output-only and is never re-scanned.
    """
    out = []
    i = 0
    n = len(text)
    while i < n:
        matched = False
        for find, replace in ops:
            flen = len(find)
            # find is guaranteed non-empty; compare against original text.
            if text[i:i + flen] == find:
                out.append(replace)
                i += flen
                matched = True
                break
        if not matched:
            out.append(text[i])
            i += 1
    return "".join(out)


if __name__ == '__main__':
    assert apply_ops("a", [("a", "b"), ("b", "c")]) == "b"
    assert apply_ops("ab", [("a", "x"), ("ab", "y")]) == "xb"
    assert apply_ops("cat", [("cat", "dog"), ("dog", "bird")]) == "dog"
    assert apply_ops("hello", []) == "hello"
    print("all examples pass")
