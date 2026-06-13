"""Line-layout badness minimizer.

Suffix dynamic programming over an ordered list of word lengths.

dp[i] = minimum total badness to lay out words[i:] as the tail of the layout
        (so the final line of words[i:] is a *last* line and is free).

A line holding words[i:j] (i < j):
  used = sum(len(w) for w in words[i:j]) + (j - i - 1)
  - valid if used <= width, OR it is a single word (j - i == 1) whose
    length exceeds width (an overflowing line; treat its used length as width).
  - trailing_space = max(0, width - used)  (0 for the overflow single-word line)
  - badness = 0 if this line is the last line of the whole layout (j == n),
              else trailing_space ** 3.

Recurrence: dp[i] = min over all valid j of (line_badness(i, j) + dp[j]).

O(n^2) time, O(n) space. Python ints are arbitrary precision, so the cubes
never overflow.
"""


def min_badness(words: list[str], width: int) -> int:
    n = len(words)
    if n == 0:
        return 0

    lengths = [len(w) for w in words]

    # prefix[k] = sum of lengths of words[0:k]
    prefix = [0] * (n + 1)
    for k in range(n):
        prefix[k + 1] = prefix[k] + lengths[k]

    INF = float("inf")
    # dp[i] = min badness to lay out words[i:]; dp[n] = 0 (empty tail).
    dp = [0] * (n + 1)

    # Fill from the back so dp[j] is known before dp[i] (i < j).
    for i in range(n - 1, -1, -1):
        best = INF
        # Try every line that starts at i and ends just before j.
        for j in range(i + 1, n + 1):
            num_words = j - i
            # used length of the candidate line words[i:j]
            used = (prefix[j] - prefix[i]) + (num_words - 1)

            if used <= width:
                # Normal valid line.
                trailing = width - used
            elif num_words == 1 and lengths[i] > width:
                # Overflowing single-word line: valid, used treated as width,
                # so trailing space is 0.
                trailing = 0
            else:
                # A multi-word line that exceeds width is invalid. Because `used`
                # is strictly increasing in j, every larger j is also invalid;
                # stop extending this line.
                break

            # Last line of the whole layout is free.
            line_badness = 0 if j == n else trailing ** 3

            candidate = line_badness + dp[j]
            if candidate < best:
                best = candidate

        dp[i] = best

    return int(dp[0])


if __name__ == "__main__":
    # Sanity checks from the spec.
    assert min_badness(["aaa"], 10) == 0
    assert min_badness(["aa", "aa", "aa"], 20) == 0

    # Overflow example: 15-char word overflows on its own line (badness 0),
    # then "aa" and "aaa" on the remaining lines.
    print("overflow example:", min_badness(["aaaaaaaaaaaaaaa", "aa", "aaa"], 10))

    # A case where greedy packing loses to a balanced break.
    # "aaaa"(4) "aaaa"(4) "aaaa"(4), width 9.
    # Greedy line 1: "aaaa aaaa" used=9 trailing=0; line 2 (last): "aaaa" -> 0. Total 0.
    print("greedy-ok:", min_badness(["aaaa", "aaaa", "aaaa"], 9))

    # Force a real tradeoff: width 7, words of length 4,4,4.
    # Each pair "aaaa aaaa" = used 9 > 7 invalid, so every word is its own line.
    # Lines: 4 (trailing 3 -> 27), 4 (trailing 3 -> 27), 4 last (0). Total 54.
    print("forced singles:", min_badness(["aaaa", "aaaa", "aaaa"], 7))

    # Single word that fits: last line, free.
    assert min_badness(["a"], 1) == 0
    # Single word that overflows: still last line, free.
    assert min_badness(["aaaaa"], 2) == 0
    print("all asserts passed")
