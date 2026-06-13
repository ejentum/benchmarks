"""Line-layout badness minimizer.

Problem shape: 1-D optimal line-breaking (Knuth-Plass style) over an ordered
list of words. Optimal substructure holds because, once we fix where the first
line ends, the remaining words form an independent, identically-shaped problem.
A cubic trailing-space penalty makes the problem non-greedy (deliberately
under-filling an early line can win), so we solve it with a suffix DP rather
than a greedy line filler.

Recurrence (dp[i] = min badness to lay out words[i:]):
    dp[n] = 0
    dp[i] = min over valid j in (i, n] of  line_badness(i, j) + dp[j]

where line words[i:j] has:
    used    = sum(len(w) for w in words[i:j]) + (j - i - 1)
    trailing = max(0, width - used)
    line_badness = 0                  if j == n        (last line is free)
                 = trailing ** 3      otherwise

Validity of a line words[i:j]:
    - normal case: used <= width
    - single-word overflow exception: j == i + 1 and len(words[i]) > width is
      valid; its used length is treated as exactly width (trailing 0).
"""

from typing import List


def min_badness(words: List[str], width: int) -> int:
    n = len(words)
    if n == 0:
        return 0

    lengths = [len(w) for w in words]

    # dp[i] = minimum total badness for laying out words[i:].
    # dp[n] = 0 (empty suffix). Use a sentinel for unreachable states.
    INF = float("inf")
    dp = [INF] * (n + 1)
    dp[n] = 0

    for i in range(n - 1, -1, -1):
        # used length of words[i:j], built incrementally as j grows.
        # Start with the single word words[i] on the line (j = i + 1).
        used = lengths[i]
        for j in range(i + 1, n + 1):
            num_words = j - i
            if num_words > 1:
                # adding words[j-1]: + its length + the single joining space
                used = used + lengths[j - 1] + 1

            if num_words == 1 and lengths[i] > width:
                # single-word overflow exception: line is valid, used := width,
                # so trailing space is 0. (Does not bar longer lines from being
                # tried, but any j >= i+2 will have used > width and break.)
                trailing = 0
            elif used <= width:
                trailing = width - used
            else:
                # No valid way to extend further: adding more words only
                # increases `used`, so stop scanning j for this i.
                break

            line_badness = 0 if j == n else trailing ** 3
            cand = line_badness + dp[j]
            if cand < dp[i]:
                dp[i] = cand

    return int(dp[0])


if __name__ == "__main__":
    assert min_badness(["aaa"], 10) == 0
    assert min_badness(["aa", "aa", "aa"], 20) == 0
    assert min_badness(["aaaaaaaaaaaaaaa", "aa", "aaa"], 10) == 0

    # Two words that fit on one line -> last line is free -> 0.
    assert min_badness(["ab", "cd"], 10) == 0

    # Force a break: two words cannot share a line.
    # ["aaaaa","aaaaa"], width 5: "aaaaa" alone (used 5, trailing 0, not last,
    # badness 0) then "aaaaa" last line free -> total 0.
    assert min_badness(["aaaaa", "aaaaa"], 5) == 0

    # Force a non-zero badness: three words, width too small to combine the
    # first two, gap on the first line.
    # ["aaa","aaa","aaa"], width 4:
    #   line "aaa" (used 3, trailing 1, badness 1) x2 non-last + last free
    #   -> 1 + 1 = 2
    assert min_badness(["aaa", "aaa", "aaa"], 4) == 2

    # Greedy trap sanity: a case where packing the first line full is NOT
    # optimal under the cubic penalty. Lengths [3,3,3], width 7.
    #   Greedy: "aaa aaa" (used 7, trailing 0) then "aaa" last free -> 0.
    #   That is also optimal here (0), confirming fit.
    assert min_badness(["aaa", "aaa", "aaa"], 7) == 0

    print("all sanity checks passed")
