"""Line-layout badness minimizer.

min_badness(words, width) returns the provably minimum total badness over all
valid layouts of `words` (in order) into lines, where:
  - the last line is free (badness 0),
  - every other line has badness (trailing_space) ** 3,
  - a single word longer than `width` is a valid overflow line counted as
    used == width (trailing 0), but a MULTI-word line that overflows is invalid.

Approach: suffix dynamic programming (line-breaking DP), not greedy.
Let best[i] = minimum total badness to lay out words[i:] as a complete layout
(its own last line is the global last line, hence free). Then:
    best[n] = 0
    best[i] = min over j in (i, n]  of  line_cost(words[i:j], is_last=(j==n)) + best[j]
We only consider transitions where words[i:j] forms a *valid* line. Once a
multi-word range overflows, extending j further only makes it longer, so we
stop extending. Complexity O(n^2), trivial for n <= 400.
"""

from __future__ import annotations


def min_badness(words: list[str], width: int) -> int:
    n = len(words)
    if n == 0:
        return 0

    lengths = [len(w) for w in words]

    # best[i] = min total badness for laying out words[i:] (last line free).
    best = [0] * (n + 1)
    best[n] = 0

    for i in range(n - 1, -1, -1):
        candidate = None  # min badness found for any valid line starting at i
        used = 0          # accumulated used length of words[i:j]
        for j in range(i + 1, n + 1):
            count = j - i
            if count == 1:
                used = lengths[i]
            else:
                # extend the line by one word: previous used + 1 space + new word
                used += 1 + lengths[j - 1]

            is_last = (j == n)

            if used <= width:
                trailing = width - used
                line_cost = 0 if is_last else trailing ** 3
            elif count == 1:
                # single overflowing word: valid, used treated as width, trailing 0
                line_cost = 0
            else:
                # multi-word line that overflows: invalid. Extending j further
                # only lengthens the line, so no further valid line starts here.
                break

            total = line_cost + best[j]
            if candidate is None or total < candidate:
                candidate = total

        # candidate is always set: the single-word line words[i:i+1] is always valid.
        best[i] = candidate if candidate is not None else 0

    return best[0]


if __name__ == "__main__":
    # Sanity checks against the spec examples.
    assert min_badness(["aaa"], 10) == 0
    assert min_badness(["aa", "aa", "aa"], 20) == 0

    # ["aaaaaaaaaaaaaaa","aa","aaa"], width 10:
    # word0 (len 15) overflows alone -> badness 0; "aa aaa" fits (used 6) as last
    # line -> badness 0. Minimum total = 0.
    assert min_badness(["aaaaaaaaaaaaaaa", "aa", "aaa"], 10) == 0

    # Forced split with a penalized middle line:
    # ["aaaaa","aaaaa"], width 5 -> each word len 5; "aaaaa aaaaa" used 11 > 5 invalid.
    # Must split: line1 "aaaaa" trailing 0 badness 0 (non-last), line2 last free.
    assert min_badness(["aaaaa", "aaaaa"], 5) == 0

    # Penalty actually accrues: ["aa","aa"], width 5.
    # One line: used 2+1+2=5 <=5, last line -> 0. Two lines: line1 trailing 3
    # badness 27, line2 last 0 -> 27. Minimum = 0.
    assert min_badness(["aa", "aa"], 5) == 0

    # Force a non-zero answer: ["aaa","aaa"], width 5.
    # One line: used 3+1+3=7 > 5 invalid. Must split: line1 "aaa" trailing 2
    # badness 8 (non-last), line2 "aaa" last free -> total 8.
    assert min_badness(["aaa", "aaa"], 5) == 8

    print("all sanity checks passed")
