"""Optimal line-layout badness minimizer (Knuth-Plass-style DP).

min_badness(words, width) returns the minimum total badness over all valid
layouts of `words` into lines, where:
  - words keep their given order (no reordering),
  - words on a line are joined by single spaces,
  - used_length = sum(len) + (count - 1),
  - a line is valid if used_length <= width, EXCEPT a single word longer than
    width is also valid (overflow) with used_length treated as exactly width,
  - trailing_space = max(0, width - used_length),
  - the LAST line has badness 0,
  - every other line has badness trailing_space ** 3,
  - total badness = sum of line badnesses; we minimize it.
"""

from __future__ import annotations


def min_badness(words: list[str], width: int) -> int:
    n = len(words)
    if n == 0:
        return 0

    lengths = [len(w) for w in words]

    # Prefix sums of word lengths so the used length of words[i:j] is O(1).
    # prefix[k] = sum(lengths[0:k])
    prefix = [0] * (n + 1)
    for k in range(n):
        prefix[k + 1] = prefix[k] + lengths[k]

    INF = float("inf")

    # cost[i] = minimum badness for laying out words[i:] as the remaining lines,
    # given that the line starting at i is a fresh line. The line that ends the
    # whole layout (reaches index n) is "last" and contributes 0.
    cost = [INF] * (n + 1)
    cost[n] = 0  # nothing left to place: zero badness

    # Fill from the back so cost[j] is known before computing cost[i] (i < j).
    for i in range(n - 1, -1, -1):
        best = INF
        # Try every line that starts at i and holds words[i:j] for j in i+1..n.
        for j in range(i + 1, n + 1):
            word_count = j - i
            # used_length = sum(lengths[i:j]) + (word_count - 1)
            used = (prefix[j] - prefix[i]) + (word_count - 1)

            if used <= width:
                trailing = width - used
            elif word_count == 1:
                # Single word longer than width: valid overflow line.
                # used treated as exactly width -> trailing space 0.
                trailing = 0
            else:
                # Multi-word line exceeds width: invalid. Adding more words only
                # makes `used` larger, so no further j can be valid -> stop.
                break

            # Last line (reaches the end) is free; otherwise pay trailing**3.
            line_badness = 0 if j == n else trailing ** 3

            candidate = line_badness + cost[j]
            if candidate < best:
                best = candidate

        cost[i] = best

    result = cost[0]
    # Spec guarantees a layout always exists when words can be placed, so cost[0]
    # is finite; return it as an int.
    return int(result)


if __name__ == "__main__":
    # Sanity checks against the spec examples.
    assert min_badness(["aaa"], 10) == 0
    assert min_badness(["aa", "aa", "aa"], 20) == 0

    # Brute-force oracle for small inputs to validate the DP.
    import random

    def brute(words, width):
        n = len(words)
        L = [len(w) for w in words]
        best = [float("inf")]

        def rec(i, acc):
            if i == n:
                best[0] = min(best[0], acc)
                return
            total = -1
            for j in range(i + 1, n + 1):
                cnt = j - i
                total = sum(L[i:j]) + (cnt - 1)
                if total <= width:
                    trailing = width - total
                elif cnt == 1:
                    trailing = 0
                else:
                    break
                line_bad = 0 if j == n else trailing ** 3
                rec(j, acc + line_bad)

        rec(0, 0)
        return int(best[0])

    random.seed(0)
    for _ in range(2000):
        n = random.randint(1, 7)
        width = random.randint(1, 8)
        words = ["a" * random.randint(1, 10) for _ in range(n)]
        got = min_badness(words, width)
        exp = brute(words, width)
        assert got == exp, (words, width, got, exp)

    print("all checks passed")
