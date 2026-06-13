"""Line-layout badness minimizer.

Knuth-Plass style dynamic programming over word positions.
"""

from functools import lru_cache


def min_badness(words: list[str], width: int) -> int:
    n = len(words)
    if n == 0:
        return 0

    lengths = [len(w) for w in words]

    # Prefix sums of word lengths so a line span can be measured in O(1).
    # prefix[k] = sum(lengths[0:k])
    prefix = [0] * (n + 1)
    for k in range(n):
        prefix[k + 1] = prefix[k] + lengths[k]

    INF = float("inf")

    def line_info(i, j):
        """Info for a line holding words[i:j] (j exclusive, i < j).

        Returns (valid, trailing_space) where trailing_space is
        max(0, width - used_length). For an overflowing single word the
        line is valid and treated as used_length == width (trailing 0).
        """
        count = j - i
        # used length = sum(lengths) + (count - 1) single-space joins
        used = prefix[j] - prefix[i] + (count - 1)
        if used <= width:
            return True, width - used
        # Overflow: only valid if it is a single word longer than width.
        if count == 1:
            return True, 0  # treated as used == width
        return False, 0

    # dp[i] = minimum total badness to lay out words[i:].
    # The line that begins at i may become the last line (badness 0) if it
    # reaches the end, otherwise it contributes trailing_space ** 3.
    dp = [INF] * (n + 1)
    dp[n] = 0  # nothing left to place

    for i in range(n - 1, -1, -1):
        best = INF
        for j in range(i + 1, n + 1):
            valid, trailing = line_info(i, j)
            if not valid:
                # Once a multi-word line overflows, extending it (more words)
                # only makes it longer, so it stays invalid. Stop scanning.
                break
            if j == n:
                # This line reaches the end: it is the last line, badness 0.
                cost = 0
            else:
                cost = trailing ** 3 + dp[j]
            if cost < best:
                best = cost
        dp[i] = best

    return int(dp[0])


if __name__ == "__main__":
    assert min_badness(["aaa"], 10) == 0
    assert min_badness(["aa", "aa", "aa"], 20) == 0

    # Single 15-char word overflows on its own line (badness 0), then "aa aaa"
    # fits on one line as the last line (badness 0). Total 0.
    print(min_badness(["aaaaaaaaaaaaaaa", "aa", "aaa"], 10))

    # A case that forces a non-zero badness: force a break with leftover space.
    # words: "aaaa", "aaaa" with width 10 -> can fit both ("aaaa aaaa" = 9 <= 10)
    # as last line -> 0.
    print(min_badness(["aaaa", "aaaa"], 10))

    # Force two lines: width small enough that not all fit, and the first line
    # has trailing space.
    # "aaaaa"(5) "aaaaa"(5) width 6: line1 can only hold one word (5+5+1=11>6),
    # so line1="aaaaa" trailing=1 badness=1, line2="aaaaa" last line badness 0.
    print(min_badness(["aaaaa", "aaaaa"], 6))  # expect 1
