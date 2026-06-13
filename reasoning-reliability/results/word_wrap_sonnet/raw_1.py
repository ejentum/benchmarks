"""Line-layout badness minimizer.

Dynamic programming over word indices (Knuth-Plass style word wrap).

dp[i] = minimum total badness to lay out words[i:], given that a fresh
line starts at word i. The line that reaches the end of the word list is
the "last line" and contributes 0 badness; every other line contributes
(trailing_space ** 3).
"""


def min_badness(words: list[str], width: int) -> int:
    n = len(words)
    if n == 0:
        return 0

    lengths = [len(w) for w in words]

    # Prefix sums of word lengths so a line's raw character count is O(1).
    # prefix[k] = sum(lengths[0:k])
    prefix = [0] * (n + 1)
    for k in range(n):
        prefix[k + 1] = prefix[k] + lengths[k]

    INF = float("inf")

    # dp[i] = min badness for words[i:] when a new line begins at i.
    dp = [INF] * (n + 1)
    dp[n] = 0  # no words left to place -> no badness

    # Fill from the end backward.
    for i in range(n - 1, -1, -1):
        best = INF
        # Line holds words[i:j]; j ranges from i+1 (>=1 word) to n.
        for j in range(i + 1, n + 1):
            word_count = j - i
            # used length = sum of lengths + (word_count - 1) single spaces
            used = prefix[j] - prefix[i] + (word_count - 1)

            single_word = word_count == 1

            if used <= width:
                trailing = width - used
            elif single_word:
                # Single word longer than width: overflows, treated as
                # used == width, trailing space 0. Still a valid line.
                trailing = 0
            else:
                # Multi-word line that exceeds width is invalid. Since
                # adding more words only increases `used`, no larger j
                # for this i can be valid either -> stop scanning.
                break

            is_last_line = j == n
            line_badness = 0 if is_last_line else trailing ** 3

            sub = dp[j]
            if sub == INF:
                continue
            total = line_badness + sub
            if total < best:
                best = total

        dp[i] = best

    result = dp[0]
    # Per the spec, a layout always exists when the words can be placed.
    return int(result)


if __name__ == "__main__":
    # Sanity checks from the SPEC.
    assert min_badness(["aaa"], 10) == 0
    assert min_badness(["aa", "aa", "aa"], 20) == 0

    # Third example: 15-char word overflows alone (badness 0, used=width),
    # then "aa" and "aaa" remain.
    print(min_badness(["aaaaaaaaaaaaaaa", "aa", "aaa"], 10))

    # A case where breaking matters.
    print(min_badness(["aaaa", "bbbb", "cccc"], 9))
