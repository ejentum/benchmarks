"""Line-layout badness minimizer.

min_badness(words, width) returns the minimum total badness achievable over all
valid layouts of `words` (kept in order) into lines.

Layout rules (per spec):
  used length of a line holding words[i..j-1]:
      sum(len(w)) + (count - 1)            # single-space joins
  A line is valid iff used <= width, EXCEPT a single word longer than width is
  also valid (it overflows the margin) and its used length is treated as width.
  trailing space = max(0, width - used).
Badness:
  last line -> 0 (trailing space is free)
  any other line -> trailing_space ** 3
  total = sum of line badnesses.

Approach: O(n^2) suffix dynamic program with prefix sums for O(1) line lengths.
  dp[i] = min badness to lay out words[i:].
  dp[n] = 0.
  dp[i] = min over valid lines words[i..j-1] of cost(i, j) + dp[j], where
          cost(i, j) = 0 if j == n (this is the last line, free)
                       else trailing_space ** 3.
"""

from typing import List


def min_badness(words: List[str], width: int) -> int:
    n = len(words)
    if n == 0:
        return 0

    # Prefix sums of word lengths: pre[k] = sum(len(words[t]) for t < k).
    pre = [0] * (n + 1)
    for k in range(n):
        pre[k + 1] = pre[k] + len(words[k])

    INF = float("inf")
    # dp[i] = min total badness for words[i:]; dp[n] = 0 (nothing left to place).
    dp = [INF] * (n + 1)
    dp[n] = 0

    # Fill from the end so dp[j] is known before dp[i] (i < j).
    for i in range(n - 1, -1, -1):
        best = INF
        # Try every line that starts at i and ends just before j.
        for j in range(i + 1, n + 1):
            count = j - i
            # used = sum of lengths + (count - 1) single-space joins.
            used = (pre[j] - pre[i]) + (count - 1)

            if used <= width:
                trailing = width - used
            else:
                # Line is too long. Only a SINGLE over-width word is still a
                # valid (overflowing) line; its used length is treated as width,
                # so trailing space is 0. Any multi-word line that overflows is
                # invalid, and every longer line from i overflows too -> stop.
                if count == 1:
                    trailing = 0
                else:
                    break

            if dp[j] == INF:
                continue

            # Last line (ends at n) is free; otherwise pay trailing**3.
            line_cost = 0 if j == n else trailing ** 3
            total = line_cost + dp[j]
            if total < best:
                best = total

        dp[i] = best

    return int(dp[0])


if __name__ == "__main__":
    assert min_badness(["aaa"], 10) == 0
    assert min_badness(["aa", "aa", "aa"], 20) == 0
    # 15-char word overflows alone (badness 0), then "aa" "aaa" remain.
    # Best for remainder under width 10: put both on one line as the last line
    # -> total badness 0.
    print(min_badness(["aaaaaaaaaaaaaaa", "aa", "aaa"], 10))

    # A case that forces a real (non-zero) badness:
    # width 5, words all length 5 -> each must be its own line; last is free,
    # earlier lines have trailing 0 -> badness 0.
    assert min_badness(["aaaaa", "aaaaa", "aaaaa"], 5) == 0

    # Force trailing space cost: width 6, words "aaa","aaa" -> "aaa aaa" used=7>6,
    # so two lines: line1 "aaa" trailing=3 (badness 27), line2 "aaa" last (0).
    assert min_badness(["aaa", "aaa"], 6) == 27

    print("self-tests passed")
