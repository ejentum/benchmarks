"""Line-layout badness minimizer.

Implements `min_badness(words, width)` -> int.

Approach: exact dynamic programming over line breaks (NOT greedy packing).

The objective is to MINIMIZE the sum of cube-of-trailing-space costs, where the
last line is free. A greedy "pack as much as fits" strategy minimizes the number
of lines but does not minimize a convex (cubic) slack penalty, so it is the wrong
reading. We therefore solve it exactly with DP.

Two subtleties the DP must honor across ALL inputs, not just the easy ones:

  1. The LAST line (the one containing the final word) has badness 0. A backward
     DP where dp[i] is the cost of laying out words[i:] handles this: any line
     that reaches the end (j == n) contributes 0.

  2. The OVERFLOW exception. A single word longer than `width` is still valid on
     its own line, with its used length treated as exactly `width` (hence trailing
     space 0, badness 0). A naive DP that only permits lines with used_length <=
     width would leave such words unplaceable and fail. So a single-word line is
     ALWAYS allowed regardless of length; a MULTI-word line is allowed only when
     its used length fits within `width`.
"""


def min_badness(words, width):
    n = len(words)
    if n == 0:
        return 0

    lengths = [len(w) for w in words]

    # dp[i] = minimum total badness to lay out words[i:] as a sequence of lines,
    # where the line that contains the final word (words[n-1]) is the last line
    # and is therefore free.
    INF = float("inf")
    dp = [INF] * (n + 1)
    dp[n] = 0  # nothing left to place: zero cost.

    for i in range(n - 1, -1, -1):
        # Build lines starting at word i, extending the line word by word.
        # used_length = sum(lengths[i:j]) + (count - 1)
        used = 0
        best = INF
        for j in range(i + 1, n + 1):
            count = j - i
            used += lengths[j - 1]
            line_used = used + (count - 1)  # add the inter-word single spaces

            if count == 1:
                # Single word: always a valid line. Overflowing words (len > width)
                # are treated as used length == width -> trailing space 0.
                effective_used = line_used if line_used <= width else width
            else:
                # Multi-word line: only valid if it actually fits within width.
                if line_used > width:
                    # Adding this word (and any further word) cannot shrink the
                    # line, so no longer line starting at i is valid either. Stop.
                    break
                effective_used = line_used

            trailing = width - effective_used
            if trailing < 0:
                trailing = 0  # clamp (only reachable defensively)

            if j == n:
                # This line contains the final word -> it is the last line: free.
                line_cost = 0
            else:
                line_cost = trailing ** 3

            cand = line_cost + dp[j]
            if cand < best:
                best = cand

        dp[i] = best

    return int(dp[0])


if __name__ == '__main__':
    # Demo / sanity checks (not run on import).
    assert min_badness(["aaa"], 10) == 0
    assert min_badness(["aa", "aa", "aa"], 20) == 0
    # 15-char word overflows alone (badness 0), remaining two words fit as the
    # last line (badness 0) -> total 0.
    assert min_badness(["aaaaaaaaaaaaaaa", "aa", "aaa"], 10) == 0

    # A case where greedy would differ from optimal:
    # words of length 3,3,3 width 8. "aaa aaa" uses 7 (trailing 1), then "aaa"
    # last line free -> 1. Greedy packs the same here. Single line impossible
    # (3+3+3+2=11 > 8). All-singletons: line0 trailing 5 (125), line1 trailing 5
    # (125), line2 free -> 250. Best is 1.
    assert min_badness(["aaa", "aaa", "aaa"], 8) == 1

    print("ok")
