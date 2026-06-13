"""Line-layout badness minimizer.

Pure DP solution for the Knuth-Plass style word-wrap problem described in SPEC.md.

dp[i] = minimum total badness for laying out words[i:], where the line that holds
the final word counts as the last line (badness 0). We answer dp[0].
"""

from functools import lru_cache


def min_badness(words: list, width: int) -> int:
    n = len(words)
    if n == 0:
        return 0

    lengths = [len(w) for w in words]

    # Prefix sums of word lengths so a line's word-length sum is O(1).
    prefix = [0] * (n + 1)
    for k in range(n):
        prefix[k + 1] = prefix[k] + lengths[k]

    INF = float("inf")

    # dp[i] computed bottom-up. dp[n] == 0 (nothing left to place).
    dp = [INF] * (n + 1)
    dp[n] = 0

    for i in range(n - 1, -1, -1):
        best = INF
        # Line holds words[i:j].  word_count = j - i.
        for j in range(i + 1, n + 1):
            word_count = j - i
            # used_length = sum of word lengths + (word_count - 1) spaces
            used = (prefix[j] - prefix[i]) + (word_count - 1)

            if used > width:
                # A single word longer than width is allowed (it overflows; used
                # is treated as exactly width, trailing space 0). Any line with
                # more than one word that overflows is invalid, and extending the
                # line further (larger j) only makes it longer, so we can stop.
                if word_count == 1:
                    used = width  # overflow single word: clamp to width
                else:
                    break

            trailing = width - used
            if trailing < 0:
                trailing = 0  # overflowing single word

            # Last line (this line ends at the final word) has badness 0.
            line_badness = 0 if j == n else trailing ** 3

            rest = dp[j]
            if rest == INF:
                continue
            total = line_badness + rest
            if total < best:
                best = total

        dp[i] = best

    result = dp[0]
    # Per the spec a layout always exists when the words can be placed at all,
    # so result should be finite here.
    return int(result)


if __name__ == '__main__':
    # Demo / sanity checks against the SPEC examples.
    assert min_badness(["aaa"], 10) == 0
    assert min_badness(["aa", "aa", "aa"], 20) == 0

    # Example 3: 15-char word overflows alone (badness 0), then "aa","aaa".
    # Remaining "aa","aaa" with width 10:
    #   both on one line -> last line, badness 0 -> total 0.
    print(min_badness(["aaaaaaaaaaaaaaa", "aa", "aaa"], 10))

    # A case where breaking matters.
    print(min_badness(["aaaa", "aaaa", "aaaa"], 4))
    print("ok")
