"""line-layout badness minimizer.

min_badness(words, width) returns the minimum total badness achievable over all
valid layouts of `words` (kept in order) into lines.

Layout rules (per spec):
  - used_length of words[i:j] = sum(len(w)) + (count - 1)   # single-space joins
  - a line is valid if used_length <= width, OR it is a single word whose length
    exceeds width (an overflow line); an overflow single-word line is valid and its
    used length is treated as exactly `width`.
  - trailing_space = max(0, width - used_length)   # clamped at 0
  - the LAST line of the layout has badness 0; every other line has badness
    trailing_space ** 3.
  - total badness = sum of line badnesses.

Solved with an O(n^2) dynamic program over suffixes:
  dp[i] = minimum badness to lay out words[i:] as their own document
          (so the final line of words[i:] is the free last line).
  Answer = dp[0].
"""

from typing import List


def min_badness(words: List[str], width: int) -> int:
    n = len(words)
    if n == 0:
        # No words -> no lines -> no badness. (Spec guarantees >=1, but be safe
        # since this file is imported and called directly.)
        return 0

    lengths = [len(w) for w in words]

    # dp[i] = min total badness for laying out words[i:] (its last line is free).
    # dp[n] = 0 (empty suffix, no lines).
    dp = [0] * (n + 1)

    # Build from the back so dp[j] is known when we compute dp[i] (i < j).
    for i in range(n - 1, -1, -1):
        best = None
        # used = used_length of the line words[i:j] as we extend j one word at a time.
        used = -1  # so that adding the first word (k=i) gives used = lengths[i]
        for j in range(i + 1, n + 1):
            # extend current line to include words[j-1]
            used += lengths[j - 1] + 1  # +len + one space (the leading -1 absorbs
            #                              the extra space for the very first word)

            words_on_line = j - i
            if used <= width:
                # normal valid line
                trailing = width - used
            elif words_on_line == 1:
                # single over-width word: valid overflow line, used treated as width,
                # trailing space treated as 0.
                trailing = 0
            else:
                # multi-word line that exceeds width and is NOT a single overflow
                # word -> invalid. Any further j only makes `used` larger, so no
                # longer line starting at i can be valid either: stop extending.
                break

            if j == n:
                # this line reaches the end -> it is the last (free) line
                line_cost = 0
            else:
                line_cost = trailing ** 3

            candidate = line_cost + dp[j]
            if best is None or candidate < best:
                best = candidate

        # `best` is guaranteed set: j = i+1 (the single word words[i]) is always a
        # valid line (either it fits, or it is a single over-width overflow line).
        dp[i] = best  # type: ignore[assignment]

    return dp[0]


if __name__ == "__main__":
    # Sanity checks against the spec examples and edge cases.
    assert min_badness(["aaa"], 10) == 0
    assert min_badness(["aa", "aa", "aa"], 20) == 0
    assert min_badness(["aaaaaaaaaaaaaaa", "aa", "aaa"], 10) == 0

    # single over-width word alone -> last line -> 0
    assert min_badness(["xxxxxxxxxxxxxxx"], 10) == 0
    # empty -> 0 (defensive)
    assert min_badness([], 10) == 0

    # forced two-line break: width 5, words of len 3 and 3 cannot share a line
    # (3+3+1=7 > 5). Line1 = "aaa" trailing 2 -> 8; line2 (last) free -> 0. Total 8.
    assert min_badness(["aaa", "aaa"], 5) == 8

    # three len-3 words, width 5: must each be its own line except last is free.
    # line1 trailing 2 ->8, line2 trailing 2 ->8, line3 (last) free. Total 16.
    assert min_badness(["aaa", "aaa", "aaa"], 5) == 16

    # duplicates: only lengths matter; two len-2 words fit on one line in width 5
    # (2+2+1=5 <= 5) -> single last line -> 0.
    assert min_badness(["bb", "bb"], 5) == 0

    print("all checks passed")
