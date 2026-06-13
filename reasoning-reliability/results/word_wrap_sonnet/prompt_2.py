"""Line-layout badness minimizer.

Minimizes total layout badness (Knuth-Plass style) over ALL valid line breaks,
not the greedy "fill each line as much as possible" heuristic.

Greedy is the obvious-but-wrong reading here: packing a line as tight as
possible can force a worse trailing-space cube later in the paragraph. The
objective asks for the global minimum over every valid layout, so this uses
dynamic programming over break points.
"""

from typing import List


def min_badness(words: List[str], width: int) -> int:
    n = len(words)
    if n == 0:
        return 0

    lengths = [len(w) for w in words]

    # dp[i] = minimum total badness to lay out words[i:] optimally, given that
    # the final line of the whole paragraph (the line ending at index n) is free.
    # dp[n] = 0 (empty suffix). We fill from the back.
    INF = float("inf")
    dp = [INF] * (n + 1)
    dp[n] = 0

    for i in range(n - 1, -1, -1):
        # Try every line that starts at i and holds words[i:j] for j in (i+1..n).
        # used_length grows monotonically as we add words, so once a multi-word
        # line exceeds the width we can stop extending it.
        used = 0
        best = INF
        for j in range(i + 1, n + 1):
            count = j - i
            if count == 1:
                used = lengths[i]
            else:
                used += 1 + lengths[j - 1]  # one space + the next word

            single_overflow = (count == 1 and lengths[i] > width)

            if used > width and not single_overflow:
                # This line is invalid; adding more words only makes it longer.
                break

            # Determine this line's badness.
            if j == n:
                # Last line of the paragraph: trailing space is free.
                line_cost = 0
            elif single_overflow:
                # Overflowing single word: used length treated as exactly width,
                # so trailing space is 0 -> badness 0.
                line_cost = 0
            else:
                trailing = width - used  # >= 0 here since used <= width
                line_cost = trailing ** 3

            total = line_cost + dp[j]
            if total < best:
                best = total

            if single_overflow:
                # An overflowing single word cannot be extended with more words.
                break

        dp[i] = best

    return int(dp[0])


if __name__ == "__main__":
    assert min_badness(["aaa"], 10) == 0
    assert min_badness(["aa", "aa", "aa"], 20) == 0
    assert min_badness(["aaaaaaaaaaaaaaa", "aa", "aaa"], 10) == 0

    # Greedy-trap check: greedy would pack the first line full and pay a large
    # cube on an early break; balanced breaking does better.
    # words of length 3 each, width 7 -> two words per line uses 3+1+3=7.
    print("manual:", min_badness(["aaa", "aaa", "aaa", "aaa"], 7))
    print("all tests passed")
