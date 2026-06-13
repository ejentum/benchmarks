"""Line-layout badness minimizer.

Knuth-Plass style dynamic programming over word-break positions.

dp[i] = minimum total badness for laying out words[i..n-1].
The line that contains the very last word contributes badness 0
(trailing space on the last line is free). Every other line
contributes (trailing_space ** 3).

A line holding words[i..j-1] has:
    used_length = sum(len(w)) + (count - 1)
A line is valid if used_length <= width, with the single exception
that a single word longer than width is also valid (it overflows and
is treated as used_length == width, so trailing space 0).

We extend a candidate first line word by word. As soon as a multi-word
line exceeds width it becomes (and stays) invalid, so we stop extending.
"""

from typing import List


def min_badness(words: List[str], width: int) -> int:
    n = len(words)
    if n == 0:
        return 0

    lengths = [len(w) for w in words]

    # dp[i] = min badness for words[i:]. dp[n] = 0 (empty suffix).
    INF = float("inf")
    dp = [INF] * (n + 1)
    dp[n] = 0

    # Fill from the back so dp[j] is known when computing dp[i].
    for i in range(n - 1, -1, -1):
        best = INF
        # used_length of words[i..j-1] as we grow j.
        used = 0
        count = 0
        for j in range(i + 1, n + 1):
            # Add words[j-1] to the current line.
            if count == 0:
                used = lengths[j - 1]
            else:
                used += 1 + lengths[j - 1]  # joining space + word length
            count += 1

            # Validity check.
            if used > width:
                if count == 1:
                    # Single overflowing word: valid, treat used as width.
                    trailing = 0
                else:
                    # Multi-word line overflowed: invalid, and any longer
                    # line is also invalid, so stop extending.
                    break
            else:
                trailing = width - used

            # Cost of using words[i..j-1] as the first line.
            if j == n:
                # This is the last line: badness 0.
                line_cost = 0
                total = line_cost  # dp[n] == 0
            else:
                line_cost = trailing ** 3
                total = line_cost + dp[j]

            if total < best:
                best = total

        dp[i] = best

    return int(dp[0])


if __name__ == "__main__":
    assert min_badness(["aaa"], 10) == 0
    assert min_badness(["aa", "aa", "aa"], 20) == 0

    # Single line fits.
    assert min_badness(["a", "b", "c"], 100) == 0

    # Force a break: two words that cannot share a line.
    # "aaaaa"(5) and "bbbbb"(5) with width 5 -> each on its own line.
    # First line trailing = 0, last line free -> total 0.
    assert min_badness(["aaaaa", "bbbbb"], 5) == 0

    # Trailing space cost on a non-last line.
    # width 10, words "aa"(2),"bb"(2),"cc"(2),"dd"(2),"ee"(2)
    # all fit on one line: 2*5 + 4 = 14 > 10, so must break.
    print(min_badness(["aa", "bb", "cc", "dd", "ee"], 10))

    # Overflow example from spec.
    print(min_badness(["aaaaaaaaaaaaaaa", "aa", "aaa"], 10))

    print("ok")
