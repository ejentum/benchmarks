"""Line-layout badness minimizer.

Pure dynamic-programming solution (Knuth-Plass style) for breaking an
ordered sequence of words into lines while minimizing total badness, where
badness of a non-final line is (trailing_space ** 3) and the final line is
free (badness 0).
"""

from functools import lru_cache


def min_badness(words: list, width: int) -> int:
    n = len(words)
    if n == 0:
        return 0

    lengths = [len(w) for w in words]

    # Prefix sums of word lengths for O(1) line-length queries.
    # prefix[k] = sum(lengths[0:k])
    prefix = [0] * (n + 1)
    for k in range(n):
        prefix[k + 1] = prefix[k] + lengths[k]

    def line_cost(i, j, is_last):
        """Badness of placing words[i:j] on a single line.

        Returns None if the line is invalid (cannot legally hold these words).
        """
        count = j - i
        # used length = sum of word lengths + (count - 1) single-space joins
        total_chars = prefix[j] - prefix[i]
        used = total_chars + (count - 1)

        if used > width:
            # Allowed only as the special overflow case: exactly one word
            # whose own length exceeds the width. Treat used as width
            # (trailing space 0).
            if count == 1 and lengths[i] > width:
                used = width
            else:
                return None  # invalid line

        trailing = width - used
        if trailing < 0:
            trailing = 0

        if is_last:
            return 0
        return trailing ** 3

    # dp[i] = minimum total badness to lay out words[i:].
    # dp[n] = 0 (nothing left to place).
    dp = [0] * (n + 1)

    for i in range(n - 1, -1, -1):
        best = None
        # Try every possible end j for the line beginning at word i.
        # Word i must always be placeable as a single word (overflow rule
        # guarantees a valid line always exists), so a solution is found.
        for j in range(i + 1, n + 1):
            is_last = (j == n)
            lc = line_cost(i, j, is_last)
            if lc is None:
                # Adding more words only makes the line longer; once invalid
                # for non-overflow reasons it stays invalid. But the very
                # first word (count == 1) might be a valid overflow line even
                # though count >= 2 lines are invalid, so only break after we
                # have passed the single-word case.
                if j > i + 1:
                    break
                else:
                    # Single word i did not fit and is not an overflow word?
                    # That cannot happen: a single word with len <= width is
                    # valid, and len > width is the overflow case. So this
                    # branch is unreachable, but continue defensively.
                    continue

            candidate = lc + (dp[j] if not is_last else 0)
            # When is_last, dp[j] == dp[n] == 0 anyway, but keep it explicit.
            if best is None or candidate < best:
                best = candidate

        dp[i] = best if best is not None else 0

    return int(dp[0])


if __name__ == '__main__':
    assert min_badness(["aaa"], 10) == 0
    assert min_badness(["aa", "aa", "aa"], 20) == 0

    # Manual sanity: two words that don't fit on one line, width 5.
    # "aaa" + "aaa" used = 3+3+1 = 7 > 5 -> must split.
    # Line1: "aaa" trailing = 5-3 = 2 -> badness 8 ; line2 last -> 0. Total 8.
    assert min_badness(["aaa", "aaa"], 5) == 8

    # Overflow single word then remaining.
    print(min_badness(["aaaaaaaaaaaaaaa", "aa", "aaa"], 10))
    print("ok")
