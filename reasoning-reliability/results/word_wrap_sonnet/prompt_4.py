"""Line-layout badness minimizer.

Minimizes the total layout badness for wrapping `words` (in order) into lines
of a given `width`, where each non-last line contributes (trailing_space ** 3)
and the last line contributes 0.

The greedy "pack as many words as possible per line" approach does NOT minimize a
sum of cubes (leaving a little slack on several lines can beat dumping it all on
one), so this is solved with an O(n^2) dynamic program over all valid break
points rather than a single greedy pass.
"""

from typing import List


def min_badness(words: List[str], width: int) -> int:
    n = len(words)
    if n == 0:
        return 0

    # Word lengths and prefix sums for O(1) line-length queries.
    lengths = [len(w) for w in words]
    prefix = [0] * (n + 1)
    for k in range(n):
        prefix[k + 1] = prefix[k] + lengths[k]

    def used_length(i: int, j: int) -> int:
        # used length of a line holding words[i..j-1]:
        #   sum(lengths) + (count - 1 spaces)
        count = j - i
        return (prefix[j] - prefix[i]) + (count - 1)

    INF = float("inf")

    # dp[i] = minimum total badness to lay out words[i:] as a complete layout,
    # where the final line of that suffix is the last line (badness 0).
    dp = [INF] * (n + 1)
    dp[n] = 0

    # Work backwards. For each start i, try every end j (j words = i..j-1).
    for i in range(n - 1, -1, -1):
        best = INF
        for j in range(i + 1, n + 1):
            ul = used_length(i, j)

            # Validity check.
            if ul > width:
                # Only a single over-width word is allowed to exceed width;
                # any multi-word group exceeding width is invalid, and since
                # extending j further only increases ul, we can stop here.
                if j - i == 1:
                    # Over-width single word: treated as used == width,
                    # trailing 0, badness 0. Still a valid line.
                    line_badness = 0
                else:
                    break
            else:
                trailing = width - ul  # >= 0 here
                # The line is the last line of the layout iff it reaches the end.
                line_badness = 0 if j == n else trailing ** 3

            if dp[j] is INF:
                continue
            candidate = line_badness + dp[j]
            if candidate < best:
                best = candidate

        dp[i] = best

    return int(dp[0])


if __name__ == "__main__":
    # Sanity checks against the spec examples.
    assert min_badness(["aaa"], 10) == 0
    assert min_badness(["aa", "aa", "aa"], 20) == 0

    # Over-width single word example: the 15-char word overflows alone
    # (badness 0), then "aa" and "aaa" remain with width 10.
    # Options for the remainder:
    #   line "aa aaa" used=6 -> last line, badness 0  => total 0
    print(min_badness(["aaaaaaaaaaaaaaa", "aa", "aaa"], 10))

    # A case where greedy loses: forcing slack distribution.
    # words of length 3 each, width 7 -> two per line fits (3+1+3=7).
    print(min_badness(["aaa", "aaa", "aaa", "aaa", "aaa"], 7))
