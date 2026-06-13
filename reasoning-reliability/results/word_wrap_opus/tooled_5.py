"""Line-layout badness minimizer.

min_badness(words, width) returns the minimum total badness achievable over all
valid layouts of `words` (in order) into lines.

Approach: dynamic programming over word suffixes (optimal paragraph formatting /
word-wrap minimization). dp[i] is the minimum badness to lay out words[i:].
Non-last lines cost (trailing_space)**3; the last line is free; a single word
longer than `width` forms a valid line whose used length is clamped to `width`
(trailing space 0).
"""

from __future__ import annotations


def min_badness(words: list[str], width: int) -> int:
    n = len(words)
    if n == 0:
        return 0

    lengths = [len(w) for w in words]

    # prefix[k] = sum of the first k word lengths, so the total character length
    # of words[i:j] is prefix[j] - prefix[i].
    prefix = [0] * (n + 1)
    for k in range(n):
        prefix[k + 1] = prefix[k] + lengths[k]

    # dp[i] = minimum badness to lay out words[i:].  dp[n] = 0 (nothing left).
    dp = [0] * (n + 1)

    # Fill from the end so that dp[j] is known when computing dp[i] (j > i).
    for i in range(n - 1, -1, -1):
        best = None
        # Try every line that starts at word i and ends just before word j.
        for j in range(i + 1, n + 1):
            count = j - i
            # used = sum of word lengths on the line + single spaces between them.
            used = (prefix[j] - prefix[i]) + (count - 1)

            if used > width:
                # A line with a single word longer than width is still valid
                # (it overflows the margin); treat its used length as width.
                if count == 1:
                    used = width
                else:
                    # Multi-word lines that exceed width are invalid, and adding
                    # any further word only makes the line longer -> stop here.
                    break

            trailing = width - used  # >= 0 by construction
            # Last line (j == n) is free; every other line costs trailing**3.
            line_badness = 0 if j == n else trailing * trailing * trailing

            candidate = line_badness + dp[j]
            if best is None or candidate < best:
                best = candidate

        dp[i] = best if best is not None else 0

    return dp[0]


if __name__ == "__main__":
    assert min_badness(["aaa"], 10) == 0
    assert min_badness(["aa", "aa", "aa"], 20) == 0

    # ["aaaaaaaaaaaaaaa","aa","aaa"], width 10:
    # 15-char word overflows on its own line (badness 0, used clamped to width).
    # Remaining "aa","aaa": "aa aaa" = 6 used -> last line free. So line1=0,
    # line2 free -> total 0.  (Splitting them would add a positive cube.)
    assert min_badness(["aaaaaaaaaaaaaaa", "aa", "aaa"], 10) == 0

    # Force a real penalty: two short words that cannot share a line.
    # ["aaaaa","aaaaa"], width 5: each is exactly 5, "aaaaa aaaaa"=11 > 5 invalid.
    # Line1 = "aaaaa" used 5 trailing 0 -> 0; line2 last -> 0. total 0.
    assert min_badness(["aaaaa", "aaaaa"], 5) == 0

    # ["aa","aa"], width 5: together "aa aa"=5 fits -> one (last) line -> 0.
    assert min_badness(["aa", "aa"], 5) == 0

    # ["a","a","a"], width 1: each "a" alone (a+a = "a a"=3 >1). lines: each
    # trailing 0. last free. total 0.
    assert min_badness(["a", "a", "a"], 1) == 0

    # Penalty case: ["aa","aa"], width 4. "aa aa"=5>4, so two lines.
    # line1 "aa" used 2 trailing 2 -> 2**3=8; line2 last free. total 8.
    assert min_badness(["aa", "aa"], 4) == 8

    print("all assertions passed")
