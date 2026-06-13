"""Line-layout badness minimizer.

Classic word-wrap dynamic programming: choose line breaks (preserving word
order) to minimize total badness, where each non-last line costs
(trailing_space ** 3) and the last line is free.
"""


def min_badness(words, width):
    n = len(words)
    if n == 0:
        return 0

    lengths = [len(w) for w in words]

    # Prefix sums of word lengths so we can compute a line's used length in O(1).
    # prefix[k] = sum(lengths[0:k])
    prefix = [0] * (n + 1)
    for k in range(n):
        prefix[k + 1] = prefix[k] + lengths[k]

    INF = float("inf")

    # dp[i] = minimum total badness to lay out words[i:] given that the line
    # starting at word i begins a fresh line. dp[n] = 0 (nothing left).
    dp = [INF] * (n + 1)
    dp[n] = 0

    # Fill from the end backwards.
    for i in range(n - 1, -1, -1):
        best = INF
        # The first line covers words[i .. j-1] for j in (i+1 .. n).
        for j in range(i + 1, n + 1):
            num_words = j - i
            # used length = sum of word lengths + (num_words - 1) single spaces
            used = (prefix[j] - prefix[i]) + (num_words - 1)

            if used <= width:
                trailing = width - used
            else:
                # Line overflows. Only valid if it is a SINGLE word that is
                # longer than the width; such a line overflows the margin and is
                # treated as used == width (trailing space 0).
                if num_words == 1:
                    trailing = 0
                else:
                    # Multi-word line exceeds width: invalid. Since adding more
                    # words only makes the line longer, no larger j can be valid
                    # either, so stop extending this line.
                    break

            # Badness of this line: 0 if it is the last line (j == n),
            # otherwise trailing ** 3.
            if j == n:
                line_cost = 0
            else:
                line_cost = trailing ** 3

            rest = dp[j]
            if rest is INF:
                continue
            total = line_cost + rest
            if total < best:
                best = total

        dp[i] = best

    return int(dp[0])


if __name__ == "__main__":
    assert min_badness(["aaa"], 10) == 0
    assert min_badness(["aa", "aa", "aa"], 20) == 0
    # 15-char word overflows on its own line (cost 0), remaining "aa aaa"
    # ("aa aaa" = 6 chars used, fits in width 10) goes on the last line (cost 0).
    print(min_badness(["aaaaaaaaaaaaaaa", "aa", "aaa"], 10))
    # A case forcing a real break.
    print(min_badness(["aaaa", "aaaa", "aaaa"], 5))
