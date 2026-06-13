"""Line-layout badness minimizer.

Linear-sequence dynamic programming. dp[i] = minimum total badness achievable
when laying out words[i:]. The cost of a layout decomposes as: cost of the first
line (words[i:j]) plus dp[j] (the optimal layout of the remaining words). The last
line is free, which falls out naturally because the line that ends at n contributes
0 badness and dp[n] = 0.
"""

from typing import List


def min_badness(words: List[str], width: int) -> int:
    n = len(words)
    if n == 0:
        return 0

    lengths = [len(w) for w in words]

    # prefix[k] = total length of words[0:k] (sum of raw word lengths, no spaces)
    prefix = [0] * (n + 1)
    for k in range(n):
        prefix[k + 1] = prefix[k] + lengths[k]

    # dp[i] = minimum badness to lay out words[i:]; dp[n] = 0 (nothing left).
    INF = float("inf")
    dp = [INF] * (n + 1)
    dp[n] = 0

    # Fill from the back so dp[j] is known when computing dp[i] (j > i).
    for i in range(n - 1, -1, -1):
        best = INF
        # Try every line consisting of words[i:j].
        for j in range(i + 1, n + 1):
            words_on_line = j - i
            # used length = sum of word lengths + (count - 1) single spaces
            used = (prefix[j] - prefix[i]) + (words_on_line - 1)

            single_overflow = (words_on_line == 1) and (used > width)

            if used > width and not single_overflow:
                # Multi-word line that exceeds the width is invalid; any longer
                # line (larger j) is only longer, so stop extending from here.
                break

            if single_overflow:
                # Overflowing single word: treat used as exactly width, so the
                # trailing space (and hence badness) is 0.
                trailing = 0
            else:
                trailing = width - used  # >= 0 here

            # Last line is free; every other line costs trailing**3.
            line_cost = 0 if j == n else trailing ** 3

            total = line_cost + dp[j]
            if total < best:
                best = total

        dp[i] = best

    return int(dp[0])


if __name__ == "__main__":
    assert min_badness(["aaa"], 10) == 0
    assert min_badness(["aa", "aa", "aa"], 20) == 0

    # The 15-char word overflows on its own line (badness 0), leaving ["aa","aaa"].
    # Those two fit on one line ("aa aaa" used=6 <= 10) which becomes the last line
    # (free), so total badness is 0. Putting them on separate lines would make the
    # "aa" line non-last with trailing (10-2)**3 = 512, so the minimum is 0.
    assert min_badness(["aaaaaaaaaaaaaaa", "aa", "aaa"], 10) == 0

    # A forced break: two words that cannot share a line. width=3, words "aa","aa".
    # Line1 "aa" trailing=1 -> 1; line2 "aa" is last -> 0. Total 1.
    assert min_badness(["aa", "aa"], 3) == 1

    print("all sanity checks passed")
