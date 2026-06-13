"""Line-layout badness minimizer.

Classic word-wrap / text-justification 1D dynamic program (Knuth-Plass family)
with a cubic trailing-space penalty, a free last line, and a single-word
overflow rule. See SPEC.md for the exact layout/badness semantics.

The function is pure and importable; only `min_badness` is part of the API.
"""

from __future__ import annotations


def min_badness(words: list[str], width: int) -> int:
    """Return the minimum total badness over all valid layouts of `words`.

    Layout rules (per spec):
      - A line holding words[i:j] has
            used = sum(len(w) for w in words[i:j]) + (j - i - 1)
      - The line is valid if used <= width. Exception: a single-word line
        (j - i == 1) whose word is longer than `width` is also valid and its
        used length is treated as exactly `width` (it overflows the margin).
      - trailing_space = max(0, width - used).
      - The LAST line (the one that consumes the final word) has badness 0.
      - Every other line has badness trailing_space ** 3.
      - Total badness = sum of line badnesses; we minimize over valid layouts.

    DP formulation (suffix DP):
      dp[i] = minimum badness to lay out words[i:].
      dp[n] = 0.
      dp[i] = min over j in (i, n] of  line_badness(i, j) + dp[j],
      where a line that ends at j == n is the last line (badness 0).
    """
    n = len(words)
    if n == 0:
        return 0

    lengths = [len(w) for w in words]

    # prefix[k] = total character length of words[:k] (excludes joining spaces).
    prefix = [0] * (n + 1)
    for k in range(n):
        prefix[k + 1] = prefix[k] + lengths[k]

    INF = float("inf")
    # dp[i] = min badness to lay out the suffix words[i:].
    dp = [0] * (n + 1)  # dp[n] = 0 (nothing left to place).

    # Fill from the end backwards so dp[j] is ready when computing dp[i].
    for i in range(n - 1, -1, -1):
        best = INF
        # Try every line that starts at word i and ends just before word j.
        for j in range(i + 1, n + 1):
            num_words = j - i
            used = (prefix[j] - prefix[i]) + (num_words - 1)

            if used <= width:
                trailing = width - used
            elif num_words == 1:
                # Single word longer than width: valid overflow line,
                # used treated as exactly width -> trailing space is 0.
                trailing = 0
            else:
                # Multi-word line exceeding width is invalid. Since `used`
                # only grows as j increases, no longer line can be valid
                # either, so stop extending this start position.
                break

            # The line ending at j == n is the last line and is free.
            line_badness = 0 if j == n else trailing ** 3

            candidate = line_badness + dp[j]
            if candidate < best:
                best = candidate

        dp[i] = best

    return int(dp[0])


if __name__ == "__main__":
    # Spec examples (guarded so importing the module runs no side effects).
    assert min_badness(["aaa"], 10) == 0
    assert min_badness(["aa", "aa", "aa"], 20) == 0
    assert min_badness(["aaaaaaaaaaaaaaa", "aa", "aaa"], 10) == 0

    # Single overflowing word, alone: last line -> badness 0.
    assert min_badness(["aaaaaaaaaaaaaaa"], 10) == 0

    # Two words that must split; second is last (free), first non-last pays.
    # width=5, ["abc","de"]: one line "abc de" used=3+2+1=6 > 5 invalid as a
    # pair, so break: line1 "abc" trailing 5-3=2 -> 8, line2 "de" last -> 0.
    assert min_badness(["abc", "de"], 5) == 8

    # Overflow word first (non-last, badness 0), then a forced split that pays.
    # width=4, ["aaaaaa","bb","cc"]: lengths 6,2,2.
    #   line "aaaaaa" overflow -> used=4, badness 0 (non-last).
    #   "bb cc" used=2+2+1=5 > 4 invalid -> must split.
    #   line "bb" trailing 4-2=2 -> 8 (non-last); line "cc" last -> 0.
    assert min_badness(["aaaaaa", "bb", "cc"], 4) == 8

    # Stress: 400 identical words, ensure it runs fast and returns an int.
    big = min_badness(["aa"] * 400, 10)
    assert isinstance(big, int)

    print("all asserts passed; min_badness ready")
