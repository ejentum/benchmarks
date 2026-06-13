"""Line-layout badness minimizer.

Given an ordered list of words and a line width, break the words into lines
(preserving order, single-space joins) so as to minimize total badness, where
each non-last line contributes (trailing_space ** 3) and the last line is free.

Solved with a Knuth-Plass-style dynamic program over word start positions.
"""

from functools import lru_cache
from typing import List


def min_badness(words: List[str], width: int) -> int:
    n = len(words)
    if n == 0:
        return 0

    lengths = [len(w) for w in words]

    # Prefix sums of word lengths so we can compute the sum over any range in O(1).
    # prefix[k] = sum(lengths[0:k])
    prefix = [0] * (n + 1)
    for k in range(n):
        prefix[k + 1] = prefix[k] + lengths[k]

    def line_used(i: int, j: int) -> int:
        """Used length for a line holding words[i..j-1] (i < j).

        Returns the 'used length' per the spec: sum of word lengths plus the
        single spaces between them. An overflowing single-word line (one word
        longer than width) is treated as exactly `width`.
        """
        chars = prefix[j] - prefix[i]
        gaps = (j - i) - 1
        used = chars + gaps
        if (j - i) == 1 and lengths[i] > width:
            # Single oversized word overflows the margin; treat used as width.
            return width
        return used

    def line_valid(i: int, j: int) -> bool:
        """A line words[i..j-1] is valid if it fits, with the single-word overflow
        exception."""
        if (j - i) == 1 and lengths[i] > width:
            return True  # single oversized word is allowed to overflow
        return line_used(i, j) <= width

    # dp(i): minimum total badness to lay out words[i..n-1], given that words[i]
    # begins a fresh line. dp(n) == 0 (empty suffix).
    @lru_cache(maxsize=None)
    def dp(i: int) -> int:
        if i == n:
            return 0

        best = None
        # Try every possible end of the line that starts at i: words[i..j-1].
        j = i + 1
        while j <= n:
            if not line_valid(i, j):
                # Lines only get longer as j grows; once invalid, stays invalid,
                # EXCEPT the single-word overflow case which is the very first j.
                # If the first word alone (j == i+1) is invalid that can only
                # happen when it's a multi-char fit failure, which the overflow
                # rule already permits, so we never hit that. For j > i+1, adding
                # more words only increases used length, so we can stop.
                if j == i + 1:
                    # The line with just words[i]; if this is invalid it means a
                    # multi-word situation which cannot occur for a single word.
                    # (Single word is always valid via the overflow exception.)
                    j += 1
                    continue
                break

            if j == n:
                # This line is the last line: its badness is 0.
                cost = 0
            else:
                used = line_used(i, j)
                trailing = width - used
                if trailing < 0:
                    trailing = 0
                cost = trailing ** 3

            sub = dp(j)
            total = cost + sub
            if best is None or total < best:
                best = total

            j += 1

        # best is always set because j == i+1 (single word) is always valid.
        return best if best is not None else 0

    return dp(0)


if __name__ == '__main__':
    # Demo / sanity checks (not run on import).
    assert min_badness(["aaa"], 10) == 0
    assert min_badness(["aa", "aa", "aa"], 20) == 0
    assert min_badness(["aaaaaaaaaaaaaaa", "aa", "aaa"], 10) == 0

    # A case where splitting is forced and costs something.
    # words of length 4,4,4 width 4: each must be on its own line.
    # line1 "aaaa" used=4 trailing=0 -> 0; line2 same -> 0; line3 last -> 0.
    assert min_badness(["aaaa", "aaaa", "aaaa"], 4) == 0

    # width 5, words len 4,4: line1 "aaaa" trailing=1 ->1, line2 last ->0 => 1
    assert min_badness(["aaaa", "aaaa"], 5) == 1

    # width 9, words len 4,4: could fit both "aaaa aaaa"=9 (last line, 0) -> 0
    assert min_badness(["aaaa", "aaaa"], 9) == 0

    # width 8, words len 4,4: "aaaa aaaa"=9 >8 invalid together.
    # So line1 "aaaa" trailing=4 ->64, line2 last ->0 => 64
    assert min_badness(["aaaa", "aaaa"], 8) == 64

    print("all demo assertions passed")
