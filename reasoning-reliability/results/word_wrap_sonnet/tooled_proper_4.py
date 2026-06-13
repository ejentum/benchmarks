"""Line-layout badness minimizer.

Exact dynamic-programming solution to the optimal line-breaking problem with a
cubic trailing-space penalty and a free last line.

Let dp[i] = minimum total badness to lay out words[i:] onto lines.
A line covers words[i:j] (i < j). Its cost depends only on (i, j, width) and on
whether it is the last line (j == len(words)); the cost of the rest is dp[j],
which is independent of how the prefix was broken -- this optimal substructure
is what makes the greedy per-line approach wrong and the DP correct.

    dp[n] = 0
    dp[i] = min over valid j of (line_cost(i, j) + dp[j])

O(n^2) transitions; n <= 400.
"""

from typing import List


def min_badness(words: List[str], width: int) -> int:
    n = len(words)
    if n == 0:
        return 0

    lengths = [len(w) for w in words]

    # dp[i] = min total badness for laying out words[i:]; dp[n] = 0 (nothing left).
    dp = [0] * (n + 1)

    # Fill backward so dp[j] is already known when computing dp[i] (j > i).
    for i in range(n - 1, -1, -1):
        best = None
        used = -1  # becomes lengths[i] (no leading space) when the first word is added
        for j in range(i + 1, n + 1):
            # Extend the current line to include words[i:j]. Adding word (j-1):
            #   first word: used = lengths[i]
            #   later word: used += 1 (space) + lengths[j-1]
            if j == i + 1:
                used = lengths[i]
            else:
                used += 1 + lengths[j - 1]

            single_word = (j == i + 1)

            if used > width:
                if single_word:
                    # A lone word longer than width is a VALID overflow line:
                    # its used length is treated as exactly `width`, so trailing
                    # space is 0 and (because it is non-last) badness is 0**3 = 0.
                    # If it is also the last line, badness is 0 anyway.
                    line_cost = 0
                    cand = line_cost + dp[j]
                    if best is None or cand < best:
                        best = cand
                # Any further extension (multi-word, used only grows) is invalid,
                # so no larger j can yield a valid line. Stop extending.
                break

            # Valid line that fits within width.
            if j == n:
                line_cost = 0  # last line: trailing space is free
            else:
                trailing = width - used  # used <= width here, so trailing >= 0
                line_cost = trailing ** 3

            cand = line_cost + dp[j]
            if best is None or cand < best:
                best = cand

        # best is always set: j = i+1 (the single word alone) is always reachable,
        # either as a fitting line or as a valid overflow line.
        dp[i] = best

    return dp[0]


if __name__ == "__main__":
    # Spec examples.
    assert min_badness(["aaa"], 10) == 0
    assert min_badness(["aa", "aa", "aa"], 20) == 0

    # Reference brute force (enumerate every break set) as a correctness oracle.
    def _brute(words, width):
        n = len(words)
        lengths = [len(w) for w in words]
        best = [None]

        def rec(i, acc):
            if i == n:
                if best[0] is None or acc < best[0]:
                    best[0] = acc
                return
            used = -1
            for j in range(i + 1, n + 1):
                if j == i + 1:
                    used = lengths[i]
                else:
                    used += 1 + lengths[j - 1]
                if used > width:
                    if j == i + 1:  # valid overflow single word
                        line_cost = 0
                        rec(j, acc + line_cost)
                    break
                if j == n:
                    line_cost = 0
                else:
                    line_cost = (width - used) ** 3
                rec(j, acc + line_cost)

        rec(0, 0)
        return best[0]

    import random
    random.seed(7)
    for _ in range(3000):
        w = random.randint(1, 8)
        ws = ["a" * random.randint(1, w + 2) for _ in range(random.randint(1, 7))]
        wd = random.randint(1, w)
        assert min_badness(ws, wd) == _brute(ws, wd), (ws, wd, min_badness(ws, wd), _brute(ws, wd))

    print("all checks passed")
