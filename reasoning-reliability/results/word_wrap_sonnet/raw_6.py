"""Line-layout badness minimizer.

Pure dynamic-programming solution. ``dp[i]`` is the minimum total badness for
laying out ``words[i:]``, given that the line that ends at the final word is the
layout's last line (badness 0). We extend each line greedily only as far as it
stays valid, so the inner loop short-circuits once a prefix overflows.
"""

from typing import List


def min_badness(words: List[str], width: int) -> int:
    n = len(words)
    if n == 0:
        return 0

    lengths = [len(w) for w in words]

    # dp[i] = minimum total badness to lay out words[i:].
    # The line that contains the final word is the last line => badness 0.
    INF = float("inf")
    dp = [INF] * (n + 1)
    dp[n] = 0  # nothing left to place

    # Iterate from the end backwards.
    for i in range(n - 1, -1, -1):
        # Try every line that starts at i and holds words[i..j-1] (j from i+1..n).
        used = 0  # running used_length of words[i..j-1]
        for j in range(i + 1, n + 1):
            count = j - i
            # used_length = sum(lengths[i..j-1]) + (count - 1)
            if j == i + 1:
                used = lengths[i]
            else:
                used = used + 1 + lengths[j - 1]  # add a space and the next word

            is_last_line = (j == n)
            single_word = (count == 1)

            if used <= width:
                trailing = width - used
                line_badness = 0 if is_last_line else trailing ** 3
            elif single_word:
                # A single word longer than width overflows but is still valid;
                # treat used as exactly width => trailing space 0.
                line_badness = 0  # 0 ** 3 == 0, and last line is 0 too
            else:
                # Adding more words only makes it longer; no valid line beyond here.
                break

            rest = dp[j]
            if rest is INF:
                continue
            total = line_badness + rest
            if total < dp[i]:
                dp[i] = total

    return int(dp[0])


if __name__ == "__main__":
    assert min_badness(["aaa"], 10) == 0
    assert min_badness(["aa", "aa", "aa"], 20) == 0
    # 15-char word overflows on its own line (badness 0), then "aa aaa" fits on
    # the last line (badness 0) -> total 0.
    print(min_badness(["aaaaaaaaaaaaaaa", "aa", "aaa"], 10))
    # A case that forces a non-zero break.
    print(min_badness(["aaaa", "bbbb", "cccc"], 4))
