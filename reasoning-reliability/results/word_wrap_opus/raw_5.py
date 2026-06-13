"""Line-layout badness minimizer.

Classic dynamic-programming line-breaking (cubic trailing-space penalty).
dp[i] = minimum total badness to lay out words[i:] as a complete suffix,
where whichever line ends at the final word is the free "last line".
"""


def min_badness(words, width):
    n = len(words)
    if n == 0:
        return 0

    lens = [len(w) for w in words]

    # Prefix sums of word lengths so we can compute the summed length of any
    # contiguous run of words in O(1).
    #   prefix[k] = sum(lens[0:k])
    prefix = [0] * (n + 1)
    for k in range(n):
        prefix[k + 1] = prefix[k] + lens[k]

    INF = float("inf")

    # dp[i] = min badness to lay out words[i..n-1].
    # dp[n] = 0 (no words left).
    dp = [INF] * (n + 1)
    dp[n] = 0

    # Fill from the back so dp[j] is known when computing dp[i] (j > i).
    for i in range(n - 1, -1, -1):
        best = INF
        # Try placing words[i..j-1] on the current line, for j in i+1..n.
        for j in range(i + 1, n + 1):
            count = j - i
            # used length = sum of word lengths + (count - 1) single spaces
            used = (prefix[j] - prefix[i]) + (count - 1)

            is_single = (count == 1)
            single_overflow = is_single and lens[i] > width

            if used > width:
                # Only valid if it's a single word that overflows the margin.
                if single_overflow:
                    # Treat used length as exactly width -> trailing space 0.
                    effective_used = width
                else:
                    # Adding more words only makes it longer; stop extending.
                    break
            else:
                effective_used = used

            trailing = width - effective_used
            if trailing < 0:
                trailing = 0  # safety clamp (overflow case already -> 0)

            if j == n:
                # This line reaches the final word: it is the last line, free.
                line_badness = 0
            else:
                line_badness = trailing ** 3

            tail = dp[j]
            if tail is INF:
                continue
            total = line_badness + tail
            if total < best:
                best = total

        dp[i] = best

    return int(dp[0])


if __name__ == '__main__':
    assert min_badness(["aaa"], 10) == 0
    assert min_badness(["aa", "aa", "aa"], 20) == 0

    # Overflowing single word example: 15-char word on width 10.
    # Line 1: "aaaaaaaaaaaaaaa" overflows -> used treated as 10, trailing 0,
    #         but it is NOT the last line -> badness 0**3 = 0.
    # Remaining ["aa","aaa"]: "aa aaa" -> used = 2+3+1 = 6 <= 10. This is the
    #         last line -> badness 0. Total = 0.
    print(min_badness(["aaaaaaaaaaaaaaa", "aa", "aaa"], 10))

    # A case forcing nonzero badness:
    # width 5, words each length 3 -> can't share a line (3+1+3=7>5).
    # ["aaa","aaa"]: line1 "aaa" trailing 2 (not last) -> 8; line2 last -> 0.
    print(min_badness(["aaa", "aaa"], 5))  # expect 8

    # Three forced lines: ["aaa","aaa","aaa"], width 5
    # line1 trailing 2 ->8, line2 trailing 2 ->8, line3 last ->0 => 16
    print(min_badness(["aaa", "aaa", "aaa"], 5))  # expect 16

    print("ok")
