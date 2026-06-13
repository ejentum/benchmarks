"""Line-layout badness minimizer.

min_badness(words, width) returns the minimum total badness achievable over all
valid layouts of `words` (in order) into lines, where:

  - A line holding words[i..j-1] has
        used_length = sum(len(w)) + (count - 1)   # single-space joins
    and is valid when used_length <= width, OR when it is a single word longer
    than `width` (an overflowing line; its used length is treated as `width`).
  - trailing_space = max(width - used_length, 0).
  - The LAST line of the layout has badness 0; every other line has badness
        trailing_space ** 3.
  - Total badness is the sum of per-line badnesses.

Pure function, no I/O. O(n^2) dynamic programming over break points.
"""

from __future__ import annotations


def min_badness(words: list[str], width: int) -> int:
    n = len(words)
    if n == 0:
        # Not in the stated contract (1 <= len(words)), but an empty layout
        # has no lines and therefore zero badness.
        return 0

    lengths = [len(w) for w in words]

    # prefix[k] = sum of word lengths for words[0..k-1]
    prefix = [0] * (n + 1)
    for k in range(n):
        prefix[k + 1] = prefix[k] + lengths[k]

    # best[i] = minimum total badness to lay out words[i..n-1], given that the
    # final line of the whole layout (the one reaching index n) is free.
    # best[n] = 0 (nothing left to place).
    best = [0] * (n + 1)

    for i in range(n - 1, -1, -1):
        cur = None  # sentinel: no valid continuation found yet
        # Try every line that starts at i and ends just before j (words[i..j-1]).
        for j in range(i + 1, n + 1):
            count = j - i
            # used_length = sum of word lengths on the line + single spaces
            used = prefix[j] - prefix[i] + (count - 1)

            if count == 1 and lengths[i] > width:
                # Overflowing single-word line: valid, used treated as width,
                # so trailing space is 0.
                trailing = 0
            elif used <= width:
                trailing = width - used
            else:
                # Line too long (and not the lone-overflow exception). Any
                # further j only adds words, so the line can never get shorter.
                break

            is_last_line = (j == n)
            line_cost = 0 if is_last_line else trailing ** 3
            candidate = line_cost + best[j]

            if cur is None or candidate < cur:
                cur = candidate

        # A valid continuation always exists: the single word words[i] alone is
        # placeable (either it fits, or it overflows under the exception).
        best[i] = cur if cur is not None else 0

    return best[0]


if __name__ == '__main__':
    # Spec examples and a couple of forcing cases.
    assert min_badness(["aaa"], 10) == 0
    assert min_badness(["aa", "aa", "aa"], 20) == 0
    assert min_badness(["aaaaaaaaaaaaaaa", "aa", "aaa"], 10) == 0
    # Forcing nonzero: lens [5,5], width 6 -> line1 trailing 1 (cube 1), line2 last.
    assert min_badness(["aaaaa", "aaaaa"], 6) == 1
    # Exact-fill lines cost 0 even when split.
    assert min_badness(["aaaaa", "aaaaa"], 5) == 0
    print("ok")
