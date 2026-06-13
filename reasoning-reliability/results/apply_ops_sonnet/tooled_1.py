"""apply_ops: single forward pass text rewriter.

Applies an ordered list of (find, replace) operations to ``text`` in one
left-to-right pass over the ORIGINAL input. At each cursor position the first
op (by list order, NOT longest match) whose ``find`` matches the original text
at that position fires: its ``replace`` is appended to the output and the cursor
advances past the matched span in the original text. Emitted replacement text is
output only and is never re-scanned.
"""


def apply_ops(text, ops):
    # Precompute lengths once; find strings are guaranteed non-empty by the spec.
    op_list = [(find, replace, len(find)) for find, replace in ops]

    out = []          # collected output fragments, joined at the end
    i = 0
    n = len(text)

    while i < n:
        for find, replace, flen in op_list:
            # text[i:i+flen] == find, without building a slice each time.
            if text.startswith(find, i):
                out.append(replace)
                i += flen
                break
        else:
            # No op matched at i: emit the single original char, advance by 1.
            out.append(text[i])
            i += 1

    return "".join(out)


if __name__ == "__main__":
    assert apply_ops("a", [("a", "b"), ("b", "c")]) == "b"
    assert apply_ops("ab", [("a", "x"), ("ab", "y")]) == "xb"
    assert apply_ops("cat", [("cat", "dog"), ("dog", "bird")]) == "dog"
    assert apply_ops("hello", []) == "hello"
    # Edge: empty text.
    assert apply_ops("", [("a", "b")]) == ""
    # Edge: empty replacement.
    assert apply_ops("axb", [("x", "")]) == "ab"
    # Boundary: find longer than remaining text never matches.
    assert apply_ops("ab", [("abc", "z")]) == "ab"
    # No re-scan: emitted text containing a find is not rewritten.
    assert apply_ops("a", [("a", "aa"), ("aa", "z")]) == "aa"
    print("all tests passed")
