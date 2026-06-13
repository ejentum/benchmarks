"""Line-layout badness minimizer.

Optimal dynamic programming over suffixes (Knuth-Plass style), NOT greedy
line-filling. Greedy minimizes line count but not the cubic trailing-space
penalty; the objective demands the global minimum over all valid layouts, so
slack must be distributed optimally rather than packed.

Care is taken with the single-word overflow exception: a line holding one word
longer than `width` is valid (trailing space treated as 0), but a multi-word
line whose used length exceeds `width` is invalid. The inner loop therefore
always admits the single-word start, then stops extending once a 2+-word line
overflows.
"""


def min_badness(words, width):
    n = len(words)
    if n == 0:
        return 0

    lengths = [len(w) for w in words]

    # prefix[k] = sum of lengths of words[0:k]
    prefix = [0] * (n + 1)
    for k in range(n):
        prefix[k + 1] = prefix[k] + lengths[k]

    # dp[i] = minimum total badness to lay out words[i:] as the remaining
    # lines, where the final line produced is the document's last line.
    # dp[n] = 0 (nothing left to place).
    INF = float("inf")
    dp = [INF] * (n + 1)
    dp[n] = 0

    # Build from the back so dp[j] is known when computing dp[i] (i < j).
    for i in range(n - 1, -1, -1):
        best = INF
        # Try every line that starts at word i and ends just before word j.
        j = i + 1
        while j <= n:
            count = j - i
            # sum of word lengths on this line + single-space joins
            used = (prefix[j] - prefix[i]) + (count - 1)

            if count == 1:
                # Single-word line is ALWAYS valid.
                if lengths[i] > width:
                    # Overflow exception: treat used as exactly width.
                    trailing = 0
                else:
                    trailing = width - used
            else:
                # Multi-word line is valid only if it fits.
                if used > width:
                    # This line and all longer extensions are invalid.
                    break
                trailing = width - used

            # trailing is already >= 0 in every reachable branch, but clamp
            # defensively to honor the spec's "clamped to a minimum of 0".
            if trailing < 0:
                trailing = 0

            tail = dp[j]
            if tail != INF:
                if j == n:
                    # This is the document's last line: its badness is 0.
                    line_badness = 0
                else:
                    line_badness = trailing ** 3
                cand = line_badness + tail
                if cand < best:
                    best = cand

            j += 1

        dp[i] = best

    return int(dp[0])


if __name__ == "__main__":
    # Spec examples.
    print(min_badness(["aaa"], 10))                      # 0
    print(min_badness(["aa", "aa", "aa"], 20))           # 0
    print(min_badness(["aaaaaaaaaaaaaaa", "aa", "aaa"], 10))  # last two fit: 0

    # Slack-distribution check: cubic penalty should beat greedy packing.
    # Greedy would pack the first three on line 1 (trailing big) then the rest;
    # optimal spreads slack. Verify it returns an int and is finite.
    print(min_badness(["aaaa", "aaaa", "aaaa", "aaaa", "aaaa", "aaaa"], 10))
