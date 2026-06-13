"""Line-layout badness minimizer.

min_badness(words, width) returns the minimum total badness over all valid
layouts of `words` (kept in order) into lines.

Badness model:
  - A line holding words[i..j-1] has used_length = sum(len) + (count - 1).
  - Valid if used_length <= width, OR it is a single word longer than width
    (an overflow line; treat its used_length as exactly width).
  - trailing_space = max(0, width - used_length).
  - The last line costs 0; every other line costs trailing_space ** 3.
"""


def min_badness(words: list[str], width: int) -> int:
    n = len(words)
    if n == 0:
        return 0

    lengths = [len(w) for w in words]

    # prefix[k] = sum of the first k word lengths, so the sum of lengths for
    # words[i..j-1] is prefix[j] - prefix[i].
    prefix = [0] * (n + 1)
    for k in range(n):
        prefix[k + 1] = prefix[k] + lengths[k]

    INF = float("inf")

    # dp[i] = minimum total badness for laying out words[i:].
    # dp[n] = 0 (no words left to place).
    dp = [INF] * (n + 1)
    dp[n] = 0

    # Fill backward. For each start i, try every end j (line = words[i..j-1]).
    for i in range(n - 1, -1, -1):
        count = 0
        best = INF
        for j in range(i + 1, n + 1):
            count = j - i
            used = (prefix[j] - prefix[i]) + (count - 1)

            if used > width:
                # The only valid way to exceed width is a single overflow word.
                if count == 1:
                    # Overflow single-word line: treat used as width -> trailing 0.
                    line_cost = 0 if j == n else 0  # cube of 0 is 0 either way
                    cand = line_cost + dp[j]
                    if cand < best:
                        best = cand
                # Adding more words only makes `used` larger; stop extending.
                break

            trailing = width - used
            # Last line (j == n) is free; otherwise pay trailing ** 3.
            line_cost = 0 if j == n else trailing ** 3
            cand = line_cost + dp[j]
            if cand < best:
                best = cand

        dp[i] = best

    return int(dp[0])


if __name__ == "__main__":
    # Trace / sanity checks against the spec examples.
    assert min_badness(["aaa"], 10) == 0
    assert min_badness(["aa", "aa", "aa"], 20) == 0

    # 15-char word overflows on its own line (badness 0), then "aa aaa".
    # width=10: best continuation of ["aa","aaa"] is one line "aa aaa"
    # used = 2+3+1 = 6 <= 10; it is the last line -> cost 0. Total 0.
    print(min_badness(["aaaaaaaaaaaaaaa", "aa", "aaa"], 10))

    # Force a real break: width small enough that words can't share the last line.
    # ["aaa","bbb"] width=4: can't fit both (3+3+1=7>4). Line1="aaa" trailing
    # 4-3=1 cube=1 (non-last); line2="bbb" last -> 0. Total 1.
    assert min_badness(["aaa", "bbb"], 4) == 1

    # Single overflow word alone is the last line -> 0.
    assert min_badness(["aaaaaa"], 3) == 0

    print("ok")
