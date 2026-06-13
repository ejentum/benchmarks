def apply_ops(text, ops):
    """Apply ordered (find, replace) operations in a single left-to-right pass.

    Matching is always done against the ORIGINAL ``text``. At each cursor
    position the first op (in list order) whose ``find`` exactly matches the
    original text at that position fires: its ``replace`` is appended to the
    output and the cursor advances past the matched span. Emitted replacement
    text is output-only and is never re-scanned. If no op matches, the single
    original character is copied and the cursor advances by one.
    """
    out = []
    i = 0
    n = len(text)
    while i < n:
        for find, replace in ops:
            flen = len(find)
            if text[i:i + flen] == find:
                out.append(replace)
                i += flen
                break
        else:
            out.append(text[i])
            i += 1
    return "".join(out)


if __name__ == '__main__':
    assert apply_ops("a", [("a", "b"), ("b", "c")]) == "b"
    assert apply_ops("ab", [("a", "x"), ("ab", "y")]) == "xb"
    assert apply_ops("cat", [("cat", "dog"), ("dog", "bird")]) == "dog"
    assert apply_ops("hello", []) == "hello"
    print("ok")
