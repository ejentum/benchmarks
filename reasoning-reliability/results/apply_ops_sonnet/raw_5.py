def apply_ops(text, ops):
    """Apply ordered (find, replace) operations in a single left-to-right pass.

    Matching is always done against the original ``text``. At each cursor
    position, the first op (in list order) whose ``find`` matches the original
    text starting there fires: its ``replace`` is appended to the output and the
    cursor advances past the matched span in the original text. Emitted
    replacement text is output-only and is never re-scanned. If no op matches,
    the single original character is emitted and the cursor advances by 1.
    """
    out = []
    i = 0
    n = len(text)
    while i < n:
        fired = False
        for find, replace in ops:
            flen = len(find)
            # find is guaranteed non-empty per spec; compare against original text.
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
    print("ok")
