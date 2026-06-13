"""Line-layout badness minimizer (Knuth-style optimal line breaking).

min_badness(words, width) returns the minimum total badness achievable over all
valid layouts of `words` (kept in order) into lines, where:
  - a line holding words[i..j-1] has used_length = sum(len) + (k-1) joins,
  - the line is valid if used_length <= width, OR it is a single word longer than
    width (an overflowing single-word line: valid, used treated as width),
  - the LAST line of the layout is free (badness 0),
  - every other line has badness (trailing_space)**3, trailing_space >= 0.

Approach: suffix DP. dp[i] = min badness to lay out words[i:], where the final
line of that suffix is the true last line of the whole layout (and thus free).
Lines that end before the final word are non-last and cost trailing**3.
O(n^2) with prefix sums; pure integer arithmetic (no overflow in Python ints).
"""

from typing import List


def min_badness(words: List[str], width: int) -> int:
    n = len(words)
    if n == 0:
        return 0

    # Prefix sums of word lengths: pref[k] = sum(len(words[0..k-1])).
    lengths = [len(w) for w in words]
    pref = [0] * (n + 1)
    for k in range(n):
        pref[k + 1] = pref[k] + lengths[k]

    INF = float("inf")

    # dp[i] = min total badness to lay out words[i:] with its final line being
    # the last line of the layout (free). dp[n] = 0 (no words left).
    dp = [0] * (n + 1)

    for i in range(n - 1, -1, -1):
        best = INF
        # Try every line that starts at i and ends just before j (words[i..j-1]).
        for j in range(i + 1, n + 1):
            num_words = j - i
            # used_length = sum of word lengths in the line + (num_words - 1) joins
            used = (pref[j] - pref[i]) + (num_words - 1)

            if used <= width:
                trailing = width - used
            elif num_words == 1 and lengths[i] > width:
                # Overflowing single-word line: valid, used treated as width.
                trailing = 0
            else:
                # Line cannot hold these words validly; longer lines only get worse.
                break

            if j == n:
                # This line is the true last line of the layout -> free.
                line_cost = 0
            else:
                line_cost = trailing ** 3

            candidate = line_cost + dp[j]
            if candidate < best:
                best = candidate

        dp[i] = best

    # A valid layout always exists (each word can sit on its own line), so dp[0]
    # is finite; return it as an int.
    return int(dp[0])


if __name__ == "__main__":
    assert min_badness(["aaa"], 10) == 0
    assert min_badness(["aa", "aa", "aa"], 20) == 0
    # 15-char word overflows alone (0), then "aa aaa" is the last line (free) -> 0
    assert min_badness(["aaaaaaaaaaaaaaa", "aa", "aaa"], 10) == 0

    # Force a non-trivial wrap: two words that cannot share a line.
    # ["aaaa","aaaa"], width=5: can't fit both (4+4+1=9>5). First line trailing
    # = 5-4 = 1 -> 1**3 = 1; second line is last (free) -> total 1.
    assert min_badness(["aaaa", "aaaa"], 5) == 1

    # Empty-string word counts as a word (len 0) and still takes a join space.
    assert min_badness([""], 10) == 0
    assert min_badness(["", "aa"], 10) == 0  # used = 0+2+1 = 3, one (last) line

    # Single overflowing word on its own (last line) -> 0.
    assert min_badness(["x" * 100], 10) == 0

    print("all self-checks passed")
