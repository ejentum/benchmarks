"""Single-pass text operation engine.

Applies an ordered list of (find, replace) pairs to ``text`` in one
left-to-right pass over the ORIGINAL input. At each cursor position the
FIRST op (in list order, not longest-match) whose ``find`` matches the
original text at that position fires: its ``replace`` is emitted and the
cursor advances past the matched span. Emitted text is output-only and is
never re-scanned, so a replacement can never trigger a further match.
"""


def apply_ops(text, ops):
    """Apply ordered (find, replace) ops to ``text`` in a single pass.

    Matching is always done against the ORIGINAL ``text``. At each cursor
    position ``i``, the first op in ``ops`` whose ``find`` satisfies
    ``text[i:i+len(find)] == find`` fires: ``replace`` is appended to the
    output and the cursor advances by ``len(find)``. If no op matches, the
    single character ``text[i]`` is appended and the cursor advances by 1.

    Args:
        text: The original string to transform.
        ops: Ordered list of ``(find, replace)`` pairs. Every ``find`` is a
            non-empty string; ``replace`` may be any string, including "".

    Returns:
        The transformed string.
    """
    out = []          # output fragments, joined once at the end
    i = 0             # cursor over the ORIGINAL text (never re-scans output)
    n = len(text)

    while i < n:
        for find, replace in ops:
            flen = len(find)
            # Compare against the original text only. The slice never reads
            # past the end, so a `find` longer than the remaining input
            # simply cannot match. List order means the FIRST matching op
            # wins, regardless of length.
            if text[i:i + flen] == find:
                out.append(replace)
                i += flen          # advance past the matched ORIGINAL span
                break
        else:
            # No op matched at this position: emit one original character.
            out.append(text[i])
            i += 1

    return "".join(out)


if __name__ == "__main__":
    assert apply_ops("a", [("a", "b"), ("b", "c")]) == "b"
    assert apply_ops("ab", [("a", "x"), ("ab", "y")]) == "xb"
    assert apply_ops("cat", [("cat", "dog"), ("dog", "bird")]) == "dog"
    assert apply_ops("hello", []) == "hello"
    # Empty replace deletes the matched span.
    assert apply_ops("aXb", [("X", "")]) == "ab"
    print("ok")
