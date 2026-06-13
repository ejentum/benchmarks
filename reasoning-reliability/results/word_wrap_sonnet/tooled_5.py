"""Line-layout badness minimizer.

Classic optimal line-breaking (word-wrap) dynamic program.

`dp[i]` = minimum total badness to lay out words[i:] as a sequence of lines,
where the line that ends at the final word is the (free) last line.

A line holding words[i..j-1] has:
    used_length = sum(len(w)) + (count - 1)
A line is valid if used_length <= width, with the exception that a single word
longer than width is also valid (an overflowing line) and is treated as
used_length == width (trailing space 0).
trailing_space = max(width - used_length, 0)
Non-last lines cost trailing_space ** 3; the last line costs 0.
"""

from __future__ import annotations


def min_badness(words: list[str], width: int) -> int:
    n = len(words)
    if n == 0:
        return 0

    lengths = [len(w) for w in words]

    # dp[i] = min badness to lay out words[i:]; dp[n] = 0 (empty suffix).
    INF = float("inf")
    dp = [INF] * (n + 1)
    dp[n] = 0

    # Build each line starting at i, extending word by word to j-1.
    for i in range(n - 1, -1, -1):
        # used_length for line words[i..j-1]; start with the single word i.
        used = lengths[i]
        j = i + 1
        while j <= n:
            count = j - i
            if count == 1 and used > width:
                # Single word longer than width: valid overflow line, used = width.
                effective_used = width
            else:
                if used > width:
                    # Multi-word line that does not fit: no further extension fits.
                    break
                effective_used = used

            trailing = width - effective_used
            if trailing < 0:
                trailing = 0

            if j == n:
                # This line reaches the end -> it is the last line, badness 0.
                line_cost = 0
            else:
                line_cost = trailing ** 3

            cand = line_cost + dp[j]
            if cand < dp[i]:
                dp[i] = cand

            # Extend the line to include word j (a space + that word's length).
            if j < n:
                used += 1 + lengths[j]
            j += 1

    return int(dp[0])


if __name__ == "__main__":
    assert min_badness(["aaa"], 10) == 0
    assert min_badness(["aa", "aa", "aa"], 20) == 0
    # 15-char word overflows alone (cost 0), then "aa aaa" fits on the last line (cost 0).
    print(min_badness(["aaaaaaaaaaaaaaa", "aa", "aaa"], 10))
    # A case where greedy fails: cubic penalty rewards balancing.
    print(min_badness(["aaa", "aaa", "aaa", "aaa"], 6))
