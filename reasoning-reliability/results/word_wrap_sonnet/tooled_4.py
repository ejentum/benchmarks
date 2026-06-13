"""Line-layout badness minimizer.

min_badness(words, width) returns the minimum total badness achievable when
laying out `words` (in order) into lines, where every line except the last
pays a cubic trailing-space penalty.

Approach: 1D dynamic programming over word suffixes.

  dp[i] = minimum total badness to lay out words[i:], given that the line
          STARTING at word i is a fresh line.

A line covering words[i..j-1] (0 <= i < j <= n):

  used = sum(len(w) for w in words[i:j]) + (j - i - 1)   # single-space joins

  Validity:
    - if it holds a single word (j - i == 1) longer than width, it is valid
      and overflows; treat used as exactly `width`.
    - otherwise it is valid iff used <= width.
    - a multi-word line with used > width is INVALID.

  trailing = max(0, width - used)   # overflow single-word line -> 0

  badness:
    - 0 if this line is the LAST line of the layout (i.e. j == n)
    - trailing ** 3 otherwise

Transition:
  dp[i] = min over valid j of ( badness(i, j) + dp[j] ),  with dp[n] = 0.

Optimal substructure holds because each line's badness depends only on its
own word segment, so the suffix cost dp[j] is independent of how words[i:j]
were placed. Complexity O(n^2), trivial for n <= 400.
"""


def min_badness(words, width):
    n = len(words)
    if n == 0:
        return 0

    lengths = [len(w) for w in words]

    # prefix[k] = sum of word lengths for words[0:k]; lets us get a segment
    # sum in O(1): sum(lengths[i:j]) == prefix[j] - prefix[i].
    prefix = [0] * (n + 1)
    for k in range(n):
        prefix[k + 1] = prefix[k] + lengths[k]

    INF = float("inf")
    # dp[i] = min badness for words[i:]; dp[n] (empty suffix) = 0.
    dp = [INF] * (n + 1)
    dp[n] = 0

    # Fill from the back so dp[j] is known when we compute dp[i] (i < j).
    for i in range(n - 1, -1, -1):
        best = INF
        is_single = True  # j == i + 1 is the single-word case
        for j in range(i + 1, n + 1):
            count = j - i
            used = (prefix[j] - prefix[i]) + (count - 1)

            if used > width:
                if is_single:
                    # Single word longer than width: valid, overflowing line.
                    used = width  # trailing -> 0
                else:
                    # Multi-word line exceeding width is invalid; extending the
                    # segment further only makes `used` larger, so stop.
                    break

            trailing = width - used
            if trailing < 0:
                trailing = 0  # clamp (only reachable via the overflow path)

            # Last line of the layout (reaches the end) is free.
            line_badness = 0 if j == n else trailing ** 3

            total = line_badness + dp[j]
            if total < best:
                best = total

            is_single = False

        dp[i] = best

    return int(dp[0])


if __name__ == "__main__":
    # Spec examples.
    assert min_badness(["aaa"], 10) == 0
    assert min_badness(["aa", "aa", "aa"], 20) == 0

    # Single overflowing word on its own line -> badness 0 for that line.
    print("ex3:", min_badness(["aaaaaaaaaaaaaaa", "aa", "aaa"], 10))

    # A clear case: force a non-last line with trailing space.
    # ["aa","aa"] width 10: best is one line (both fit) -> last line free -> 0.
    assert min_badness(["aa", "aa"], 10) == 0

    # Two words that cannot share a line: width 3, words "aa","aa".
    # used for "aa aa" = 2+2+1 = 5 > 3 -> must split.
    # Line1 "aa": used 2, trailing 1, badness 1**3 = 1 (not last).
    # Line2 "aa": last line, free. Total = 1.
    assert min_badness(["aa", "aa"], 3) == 1

    print("ok")
