"""Line-layout badness minimizer.

Classic Knuth-style line-breaking DP. We choose where to break the sequence of
words into lines (order preserved). Each non-last line contributes
(trailing_space ** 3) to the total badness; the last line is free.

dp[i] = minimum total badness for laying out words[i:] given that a fresh line
starts at word i. The answer is dp[0].
"""

from functools import lru_cache


def min_badness(words: list[str], width: int) -> int:
    n = len(words)
    if n == 0:
        return 0

    lengths = [len(w) for w in words]

    # prefix[k] = sum of lengths of words[0:k]
    prefix = [0] * (n + 1)
    for k in range(n):
        prefix[k + 1] = prefix[k] + lengths[k]

    INF = float("inf")

    # used length for line holding words[i..j-1] (j > i):
    #   sum(lengths) + (count - 1)
    def used_length(i: int, j: int) -> int:
        count = j - i
        return (prefix[j] - prefix[i]) + (count - 1)

    # dp[i]: min badness for words[i:], new line begins at i.
    # dp[n] = 0 (nothing left). We iterate i from n-1 down to 0.
    dp = [INF] * (n + 1)
    dp[n] = 0

    for i in range(n - 1, -1, -1):
        best = INF
        # Try every end j for the line starting at i: words[i..j-1].
        for j in range(i + 1, n + 1):
            count = j - i
            used = used_length(i, j)

            if used > width:
                # Invalid line, EXCEPT a single word longer than width is allowed
                # as an overflow line (treated as used == width, trailing 0).
                if count == 1 and lengths[i] > width:
                    used = width
                else:
                    # Multi-word line that exceeds width is invalid. Adding more
                    # words only makes it longer, so no further j can be valid.
                    break

            trailing = width - used
            if trailing < 0:
                trailing = 0  # overflow single-word line clamps to 0

            if j == n:
                # This line is the last line: its trailing space is free.
                line_badness = 0
            else:
                line_badness = trailing ** 3

            rest = dp[j]
            if rest == INF:
                continue
            total = line_badness + rest
            if total < best:
                best = total

        dp[i] = best

    # dp[0] is finite because every word can always sit alone on a line
    # (single words longer than width are valid overflow lines).
    return int(dp[0])


if __name__ == "__main__":
    assert min_badness(["aaa"], 10) == 0
    assert min_badness(["aa", "aa", "aa"], 20) == 0
    print(min_badness(["aaaaaaaaaaaaaaa", "aa", "aaa"], 10))  # expect 0

    # A case forcing a non-trivial break to exercise the cubic penalty.
    # width 6, words of length 3,3,3 -> "aaa aaa"(7) too wide, so break.
    # Layout: ["aaa"],["aaa aaa"? no] ... lines: line0 "aaa"(used3,trail3,bad27),
    # last line "aaa aaa" used7>6 invalid; so last line "aaa" then "aaa aaa"
    # cannot. Best: line0 "aaa" (bad 27), last "aaa aaa" invalid -> must split:
    # line0 "aaa"(27), line1 "aaa"(27 not last), last "aaa"(0) => 54
    # vs line0 "aaa aaa" invalid. So expect 54.
    print(min_badness(["aaa", "aaa", "aaa"], 6))  # expect 54
