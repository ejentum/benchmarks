"""Line-layout badness minimizer.

Classic optimal text-wrap dynamic program (Knuth-style), with two correctness
points the naive version gets wrong:

  1. A single word longer than `width` forms a VALID line on its own (it overflows
     the margin). Its used length is treated as exactly `width`, so trailing space
     is 0 and its badness is 0. A naive `used <= width` validity gate would reject
     such a line and wrongly conclude no layout exists.

  2. The LAST line of the layout is free (badness 0); every other line pays
     `trailing_space ** 3`. The DP must only zero out the line that actually
     contains the final word, not every line that happens to reach the end.

dp[i] = minimum total badness to lay out words[i:].
"""

from functools import lru_cache


def min_badness(words: list[str], width: int) -> int:
    n = len(words)
    if n == 0:
        return 0

    lengths = [len(w) for w in words]

    # prefix[k] = sum(lengths[0:k]); used length of words[i:j] (j-i words) is
    # (prefix[j]-prefix[i]) + (j-i-1)  == sum of lengths + spaces between them.
    prefix = [0] * (n + 1)
    for k in range(n):
        prefix[k + 1] = prefix[k] + lengths[k]

    import sys
    sys.setrecursionlimit(10000)

    @lru_cache(maxsize=None)
    def best(i: int) -> int:
        # Minimum badness to place words[i:] as a sequence of lines, where the
        # line block starting at i begins a fresh layout (its final line is free).
        if i == n:
            return 0
        result = None
        for j in range(i + 1, n + 1):
            word_count = j - i
            chars = prefix[j] - prefix[i]
            used = chars + (word_count - 1)  # single-space joins

            is_single = (word_count == 1)
            if used > width and not is_single:
                # Multi-word line that does not fit: this and any longer line are
                # only going to be worse, so we can stop extending.
                break

            if used > width and is_single:
                # Overflowing single word: treat used as width -> trailing 0.
                trailing = 0
            else:
                trailing = width - used  # >= 0 here

            if j == n:
                # This line is the last line of the whole layout: free.
                line_cost = 0
            else:
                line_cost = trailing ** 3

            total = line_cost + best(j)
            if result is None or total < result:
                result = total

        # result is never None: j = i+1 (single word) is always a valid option.
        return result

    return best(0)


if __name__ == '__main__':
    assert min_badness(["aaa"], 10) == 0
    assert min_badness(["aa", "aa", "aa"], 20) == 0
    print(min_badness(["aaaaaaaaaaaaaaa", "aa", "aaa"], 10))  # -> 0

    # Sanity: a case where splitting matters.
    # widths force trailing-space cubic penalties.
    print(min_badness(["aaaa", "aaaa", "aaaa"], 9))
