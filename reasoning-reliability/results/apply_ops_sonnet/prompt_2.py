def apply_ops(text: str, ops: list[tuple[str, str]]) -> str:
    """Apply ordered (find, replace) ops in a single left-to-right pass over the
    ORIGINAL text.

    Semantics (per spec):
      - Single pass with a cursor over the original input only.
      - At each position, ops are tried in LIST ORDER; the first op whose `find`
        exactly matches text[i:i+len(find)] fires (NOT longest-match).
      - On a fire: append `replace`, advance cursor by len(find).
      - On no match: append the single original char text[i], advance by 1.
      - Replacement text is output-only and is never re-scanned.
    """
    out = []
    i = 0
    n = len(text)
    while i < n:
        fired = False
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
    print("all examples pass")
