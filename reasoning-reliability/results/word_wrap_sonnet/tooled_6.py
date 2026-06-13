"""Line-layout badness minimizer.

min_badness(words, width) returns the minimum total badness achievable over all
valid layouts of `words` (in order) into lines, where each non-last line costs
(trailing_space ** 3) and the last line is free.

Approach: dynamic programming over suffixes. dp[i] = minimum total badness to lay
out words[i:]. A line spans words[i:j]; it is the *last* line iff j == n (cost 0),
otherwise it costs trailing_space ** 3. We pick the minimum over all valid breaks.
"""

from functools import lru_cache


def min_badness(words: list[str], width: int) -> int:
    n = len(words)
    if n == 0:
        return 0

    lengths = [len(w) for w in words]

    def line_cost(i: int, j: int, is_last: bool):
        """Cost of placing words[i:j] on one line.

        Returns the badness for this line, or None if the line is invalid.
        A line of a single word longer than width is valid (overflows the margin)
        and is treated as used_length == width (so trailing space 0).
        The last line always has badness 0.
        """
        count = j - i
        # used length = sum of word lengths + (count - 1) single-space joins
        used = sum(lengths[i:j]) + (count - 1)

        if used > width:
            # Only valid if it is a single word that overflows the margin.
            if count == 1:
                used = width  # treat overflowing single-word line as used == width
            else:
                return None  # invalid line: too wide and more than one word

        trailing = width - used
        if trailing < 0:
            trailing = 0  # clamp (defensive; covered by the used==width path above)

        if is_last:
            return 0
        return trailing ** 3

    @lru_cache(maxsize=None)
    def dp(i: int) -> int:
        # Minimum total badness to lay out words[i:].
        if i == n:
            return 0

        best = None
        # Try every line that starts at word i and spans words[i:j].
        for j in range(i + 1, n + 1):
            is_last = (j == n)
            cost = line_cost(i, j, is_last)
            if cost is None:
                # Line words[i:j] is invalid. Adding more words only makes it
                # wider, so no longer span starting at i can become valid either.
                break
            total = cost + dp(j)
            if best is None or total < best:
                best = total

        # best is always set: words[i:i+1] is a valid line on its own (a single
        # word either fits or overflows under the exception).
        return best

    result = dp(0)
    dp.cache_clear()
    return result


if __name__ == '__main__':
    assert min_badness(["aaa"], 10) == 0
    assert min_badness(["aa", "aa", "aa"], 20) == 0

    # Overflowing single word then remaining words.
    print("example 3:", min_badness(["aaaaaaaaaaaaaaa", "aa", "aaa"], 10))

    # Single word exactly at width -> last line, cost 0.
    assert min_badness(["aaaaaaaaaa"], 10) == 0

    # Single word longer than width -> last line, cost 0 (overflow, used==width).
    assert min_badness(["aaaaaaaaaaaaaaa"], 10) == 0

    # Two words that must split; first line trailing = width - len.
    # ["aaaa","bbbb"], width 4: line1="aaaa" (used 4, trailing 0, cost 0),
    # line2="bbbb" last (cost 0). Total 0. Joining them: used 4+4+1=9 > 4 invalid.
    assert min_badness(["aaaa", "bbbb"], 4) == 0

    # Force a non-trivial cube. ["aa","aa"], width 5:
    #   split: line1 "aa" used2 trailing3 -> 27; line2 last 0 => 27
    #   joined: "aa aa" used5 trailing0 last => 0  -> min is 0
    assert min_badness(["aa", "aa"], 5) == 0

    # ["aa","aa","aa"], width 5: best is two lines: "aa aa"(used5,t0,cost0)+"aa"(last)=0
    #   or "aa"(t3=27)+"aa aa"(last)=27. min=0
    assert min_badness(["aa", "aa", "aa"], 5) == 0

    # Where a break is forced and costs something:
    # ["aaa","aaa"], width 3: cannot join (3+3+1=7>3). line1 "aaa" used3 t0 cost0,
    # line2 last 0 => 0.
    assert min_badness(["aaa", "aaa"], 3) == 0

    # ["a","a","a"], width 1: each word alone, used1 t0. lines: a(0)+a(0)+a(last0)=0
    assert min_badness(["a", "a", "a"], 1) == 0

    # ["a","a"], width 3: join "a a" used3 t0 last => 0; or split a(t2=8)+a(last)=8. min 0
    assert min_badness(["a", "a"], 3) == 0

    # A real non-zero: ["a","aa"], width 3 where joining overflows.
    # join "a aa" used 1+2+1=4 >3 invalid. split: "a"(used1,t2=>8) + "aa"(last0) = 8.
    assert min_badness(["a", "aa"], 3) == 8

    print("all assertions passed")
