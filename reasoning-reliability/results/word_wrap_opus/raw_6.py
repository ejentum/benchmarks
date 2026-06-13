"""Line-layout badness minimizer.

Knuth/Plass-style dynamic programming over word indices.

`dp[i]` = minimum total badness achievable laying out words[i:], where the line
that begins at index `i` is the first of the remaining lines. We extend a line
from `i` greedily one word at a time, computing its used length incrementally,
and stop as soon as the line can no longer be valid.

Line semantics (from the spec):
  used_length = sum(len(w)) + (word_count - 1)
  A line is valid iff used_length <= width, with one exception: a line holding a
  single word longer than width is valid as an overflow line, and for badness
  purposes its used length is treated as exactly `width` (trailing space 0).
  trailing_space = max(0, width - used_length).
  The final line of the layout has badness 0; every other line has badness
  trailing_space ** 3.
"""

from functools import lru_cache


def min_badness(words: list[str], width: int) -> int:
    n = len(words)
    if n == 0:
        return 0

    lengths = [len(w) for w in words]

    # dp[i] = min badness for words[i:] (line starting at i begins the rest).
    # Iterate from the end so dp[j] is known before dp[i] (i < j).
    INF = float("inf")
    dp = [INF] * (n + 1)
    dp[n] = 0  # nothing left to lay out

    for i in range(n - 1, -1, -1):
        best = INF
        # used_length of the line words[i:j], built incrementally.
        # Start with the first word (no joining space yet).
        used = lengths[i]
        j = i + 1
        while j <= n:
            count = j - i

            if count == 1:
                # Single-word line.
                if used > width:
                    # Overflow line: valid, treated as used == width (trailing 0).
                    trailing = 0
                    valid = True
                else:
                    trailing = width - used
                    valid = True
            else:
                # Multi-word line: only valid while it fits within the margin.
                if used > width:
                    valid = False
                    trailing = None
                else:
                    valid = True
                    trailing = width - used

            if valid:
                if j == n:
                    # This is the last line -> its badness is free (0).
                    cost = 0
                else:
                    cost = trailing ** 3 + dp[j]
                if cost < best:
                    best = cost
            else:
                # Adding more words only increases the length further, so no
                # longer line starting at i can be valid. Stop extending.
                # (A single overflow word is handled above as valid; we only
                # reach this branch for multi-word lines that already exceed
                # the width.)
                break

            # Extend the line by one more word: add a join space + next length.
            if j < n:
                used += 1 + lengths[j]
            j += 1

        dp[i] = best

    return int(dp[0])


if __name__ == '__main__':
    # Quick sanity checks against the spec examples.
    assert min_badness(["aaa"], 10) == 0
    assert min_badness(["aa", "aa", "aa"], 20) == 0

    # Brute-force reference for cross-checking on small inputs.
    def brute(words, width):
        n = len(words)
        lengths = [len(w) for w in words]

        def used_len(i, j):
            return sum(lengths[i:j]) + (j - i - 1)

        best = [float("inf")]

        def rec(i, acc, lines):
            # lines: list of (i, j) breakpoints chosen so far
            if i == n:
                # compute badness: last line free
                total = 0
                for k, (a, b) in enumerate(lines):
                    ul = used_len(a, b)
                    if k == len(lines) - 1:
                        bad = 0
                    else:
                        if (b - a) == 1 and ul > width:
                            trailing = 0
                        else:
                            trailing = max(0, width - ul)
                        bad = trailing ** 3
                    total += bad
                best[0] = min(best[0], total)
                return
            for j in range(i + 1, n + 1):
                ul = used_len(i, j)
                if (j - i) == 1 and lengths[i] > width:
                    valid = True
                elif ul <= width:
                    valid = True
                else:
                    valid = False
                if valid:
                    rec(j, None, lines + [(i, j)])
                else:
                    if (j - i) > 1:
                        break

        rec(0, None, [])
        return best[0]

    import random
    random.seed(0)
    for _ in range(2000):
        m = random.randint(1, 8)
        w = random.randint(1, 12)
        ws = ["a" * random.randint(1, 14) for _ in range(m)]
        got = min_badness(ws, w)
        exp = brute(ws, w)
        assert got == exp, (ws, w, got, exp)

    print("all checks passed")
