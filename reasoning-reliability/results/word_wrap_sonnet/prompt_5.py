"""Line-layout badness minimizer.

This solves the minimum-total-badness word-wrapping problem (a Knuth-Plass-style
optimization). The trap here is that greedy packing (fill each line as full as
possible) does NOT minimize the sum of cubed trailing spaces, and the "last line
is free" rule only applies to the line that actually ends the layout. Both are
handled correctly below with a dynamic program over suffixes of `words`.
"""

from typing import List


def min_badness(words: List[str], width: int) -> int:
    n = len(words)
    if n == 0:
        return 0

    lengths = [len(w) for w in words]

    # dp[i] = minimum total badness to lay out words[i:] as a complete layout,
    # where the line that contains the final word is treated as the last line
    # (badness 0). dp[n] = 0 (empty suffix, nothing to lay out).
    INF = float("inf")
    dp = [INF] * (n + 1)
    dp[n] = 0

    # Build from the back so dp[j] is known before computing dp[i] (j > i).
    for i in range(n - 1, -1, -1):
        # Try every line that starts at word i and holds words[i:j].
        # used_length = sum of lengths in [i, j) + (count - 1) spaces.
        used = 0  # running sum of word lengths
        count = 0
        for j in range(i + 1, n + 1):
            used += lengths[j - 1]
            count += 1
            used_length = used + (count - 1)  # include single-space joins

            if count == 1:
                # A single-word line is always valid; if it overflows the margin
                # its used length is treated as exactly `width` (trailing 0).
                effective = min(used_length, width)
                valid = True
            else:
                # Multi-word lines must fit within the width to be valid.
                valid = used_length <= width
                effective = used_length
                if not valid:
                    # Once a multi-word line overflows, adding more words only
                    # makes it longer; no further j can be valid from here.
                    break

            if not valid:
                continue

            trailing = width - effective
            if trailing < 0:
                trailing = 0

            if j == n:
                # This line contains the final word: it is the last line, free.
                line_badness = 0
            else:
                line_badness = trailing ** 3

            rest = dp[j]
            if rest == INF:
                continue
            candidate = line_badness + rest
            if candidate < dp[i]:
                dp[i] = candidate

    return int(dp[0])


if __name__ == '__main__':
    assert min_badness(["aaa"], 10) == 0
    assert min_badness(["aa", "aa", "aa"], 20) == 0
    # 15-char word overflows alone (badness 0), then "aa aaa" -> last line free.
    print(min_badness(["aaaaaaaaaaaaaaa", "aa", "aaa"], 10))
    # A case where greedy would be suboptimal:
    # words forcing a choice between one very-empty line vs spreading.
    print(min_badness(["aaa", "bb", "cc", "ddddd"], 6))
