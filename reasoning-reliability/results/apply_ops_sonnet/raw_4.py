def apply_ops(text, ops):
    """Apply ordered (find, replace) operations in a single left-to-right pass
    over the ORIGINAL text.

    At each cursor position, the first op (in list order) whose `find` exactly
    matches the original text starting at the cursor fires: its `replace` is
    appended to the output and the cursor advances past the matched span in the
    original text. If no op matches, the single original character is emitted and
    the cursor advances by one. Emitted replacement text is output only and is
    never re-scanned. Priority is list order, not longest-match.
    """
    out = []
    i = 0
    n = len(text)
    while i < n:
        for find, replace in ops:
            flen = len(find)
            # find is guaranteed non-empty per spec; matching is against the
            # original text only.
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
    print("all examples pass")
