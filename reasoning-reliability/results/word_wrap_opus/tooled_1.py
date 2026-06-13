"""Line-layout badness minimizer.

min_badness(words, width) returns the minimum total badness achievable over all
valid layouts of `words` (in order) into lines, where a line's badness is the cube
of its trailing space, the final line of the layout is free (badness 0), and a
single word longer than `width` forms its own valid line whose used length is
treated as exactly `width` (trailing space 0).

Approach: suffix dynamic programming (Knuth-Plass-style line breaking).
    dp[i] = minimum badness to lay out words[i:].
    dp[n] = 0  (empty tail; also encodes "the line ending at n is the last line").
For each start i, extend a single line word by word to end index j, tracking the
used length incrementally. A multi-word line that exceeds `width` is invalid (and
so are all longer extensions, so we stop). A single word that exceeds `width` is a
valid overflowing line with trailing space 0. The line is free iff it ends the
whole layout (j == n); otherwise it costs trailing_space ** 3.
Complexity: O(n^2) time, O(n) space; exact integer arithmetic throughout.
"""


def min_badness(words: list[str], width: int) -> int:
    n = len(words)
    if n == 0:
        return 0

    lengths = [len(w) for w in words]

    # dp[i] = min total badness to lay out words[i:]; dp[n] = 0.
    INF = float("inf")
    dp = [0] * (n + 1)

    # Build from the back so dp[j] is known when computing dp[i] (j > i).
    for i in range(n - 1, -1, -1):
        best = INF
        # line_len = used length of words[i:j] = sum(lengths) + (count - 1)
        line_len = 0
        for j in range(i + 1, n + 1):
            count = j - i
            if count == 1:
                line_len = lengths[i]
            else:
                line_len += 1 + lengths[j - 1]  # add a space + the next word

            if line_len > width:
                # Overflow. Valid only as a single oversized word (used := width,
                # trailing space 0). Any multi-word overflow is invalid, and every
                # longer line from i is also invalid, so stop extending.
                if count == 1:
                    trailing = 0
                else:
                    break
            else:
                trailing = width - line_len

            # Last line of the layout (ends at n) is free.
            line_badness = 0 if j == n else trailing ** 3

            total = line_badness + dp[j]
            if total < best:
                best = total

            # After placing a single oversized word the line cannot grow further.
            if line_len > width and count == 1:
                break

        dp[i] = best

    return int(dp[0])


if __name__ == "__main__":
    assert min_badness(["aaa"], 10) == 0
    assert min_badness(["aa", "aa", "aa"], 20) == 0
    assert min_badness(["aaaaaaaaaaaaaaa", "aa", "aaa"], 10) == 0

    # Forced split: two words that cannot share a line; first line not last -> pays.
    # ["aaaaa"(5), "aaaaa"(5)], width 6: together 5+1+5=11 > 6 -> must split.
    # line1 "aaaaa" trailing 1 -> 1**3 = 1 (not last); line2 last -> 0. Total 1.
    assert min_badness(["aaaaa", "aaaaa"], 6) == 1

    # Greedy trap: packing the first line full can be worse than balancing.
    # words lengths [3,3,3], width 7.
    #   one-per-line forced? 3+1+3=7 fits two; 7+1+3=11>7. So options:
    #   [3,3][3]: line1 trailing 0 -> 0; last 0 => 0
    #   [3][3,3]: line1 trailing 4 -> 64; last 0 => 64
    #   [3][3][3]: 4**3 + 4**3 + 0 = 128
    # min = 0
    assert min_badness(["aaa", "aaa", "aaa"], 7) == 0

    # Single oversized word only.
    assert min_badness(["aaaaaaaaaa"], 3) == 0

    print("all sanity checks passed")
