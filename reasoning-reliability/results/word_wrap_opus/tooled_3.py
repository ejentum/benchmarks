"""Line-layout badness minimizer.

Pure dynamic program. dp[i] = minimum total badness to lay out words[i:],
where the final line of the whole layout is free (cost 0).

Recurrence: for a candidate line words[i:j] (i < j <= n):
  - it is the globally-last line iff j == n -> cost 0
  - otherwise its cost is trailing_space ** 3
  dp[i] = min over all valid j of (line_cost(i, j) + dp[j])
  dp[n] = 0, answer = dp[0]

Line validity / used length:
  text_len = sum(len(w) for w in words[i:j])
  used     = text_len + (j - i - 1)          # one space between adjacent words
  - A single-word line whose word length > width is valid (it overflows the
    margin); its used length is treated as exactly width (trailing space 0).
  - Any other line is valid only if used <= width.
  trailing_space = max(0, width - used)        # 0 for an overflowing single word
"""

INF = float("inf")


def min_badness(words: list[str], width: int) -> int:
    n = len(words)
    if n == 0:
        return 0

    lengths = [len(w) for w in words]

    # dp[i]: min badness for words[i:], last global line free. dp[n] = 0.
    dp = [INF] * (n + 1)
    dp[n] = 0

    # Fill from the back so dp[j] is known when computing dp[i].
    for i in range(n - 1, -1, -1):
        used = -1  # so adding the first word gives used = lengths[i]
        best = INF
        # Extend the line to include words[i..j-1] for j = i+1 .. n.
        for j in range(i + 1, n + 1):
            used += 1 + lengths[j - 1]  # +1 space (cancels the -1 seed for j=i+1)
            words_on_line = j - i

            if used <= width:
                trailing = width - used
            elif words_on_line == 1:
                # Single oversize word: valid, used treated as exactly width.
                trailing = 0
            else:
                # Multi-word line that exceeds width: invalid. Any longer line
                # is also invalid (used only grows), so stop extending.
                break

            if j == n:
                line_cost = 0  # last line is free
            else:
                line_cost = trailing ** 3

            cand = line_cost + dp[j]
            if cand < best:
                best = cand

        dp[i] = best

    return dp[0]


if __name__ == "__main__":
    # Spec examples + boundary checks (Phase 2/4 falsification traces).
    assert min_badness(["aaa"], 10) == 0
    assert min_badness(["aa", "aa", "aa"], 20) == 0
    # Oversize word on its own line is non-last with trailing 0 -> cost 0;
    # remaining two words fit together on the last line -> 0.
    assert min_badness(["aaaaaaaaaaaaaaa", "aa", "aaa"], 10) == 0
    # Forced penalty: two len-3 words, width 4 -> first line trailing 1 -> 1**3 = 1.
    assert min_badness(["aaa", "aaa"], 4) == 1
    # width == 1, all len-1 words: every line trailing 0 -> 0.
    assert min_badness(["a", "b", "c"], 1) == 0
    # Exact fill: word length == width -> trailing 0.
    assert min_badness(["abcde", "abcde"], 5) == 0
    # Single oversize word as the only (last) line -> 0.
    assert min_badness(["abcdefgh"], 3) == 0
    # Empty-string words occupy slots but add 0 length.
    assert min_badness(["", "", ""], 5) == 0
    # Larger forced-penalty: 3 len-4 words, width 4 -> two leading lines trailing 0
    # (each its own line) -> 0; but width 5 -> trailing 1 each non-last line.
    assert min_badness(["aaaa", "aaaa", "aaaa"], 5) == 1 + 1  # two non-last lines
    # Stress: 400 words length 1, width 1 -> all own lines, all trailing 0 -> 0.
    assert min_badness(["a"] * 400, 1) == 0
    print("all assertions passed")
