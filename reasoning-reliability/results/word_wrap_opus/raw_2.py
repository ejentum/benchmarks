"""Line-layout badness minimizer.

Dynamic programming over word indices. dp[i] = minimum total badness for
laying out words[i:], where the final line of that suffix (the one reaching
the end) gets badness 0 per the spec.
"""


def min_badness(words: list[str], width: int) -> int:
    n = len(words)
    if n == 0:
        return 0

    lengths = [len(w) for w in words]

    # Prefix sums of word lengths so a line's summed word-length is O(1).
    prefix = [0] * (n + 1)
    for k in range(n):
        prefix[k + 1] = prefix[k] + lengths[k]

    INF = float("inf")

    # dp[i] = min badness to lay out words[i:] (last reached line has badness 0).
    dp = [INF] * (n + 1)
    dp[n] = 0

    # Fill from the back. For line words[i..j-1]:
    #   count        = j - i
    #   sum_lengths  = prefix[j] - prefix[i]
    #   used_length  = sum_lengths + (count - 1)
    # Validity:
    #   - used_length <= width  -> normal, trailing = width - used_length
    #   - count == 1 and single word longer than width -> overflow, trailing = 0
    # Last line of whole layout (j == n) contributes badness 0.
    for i in range(n - 1, -1, -1):
        best = INF
        for j in range(i + 1, n + 1):
            count = j - i
            used = (prefix[j] - prefix[i]) + (count - 1)

            if used <= width:
                trailing = width - used
            elif count == 1:
                # Single overflowing word: valid, treated as used == width.
                trailing = 0
            else:
                # Multi-word line exceeds width: invalid. Adding more words
                # only makes `used` larger, so no further j can be valid.
                break

            rest = dp[j]
            if rest == INF:
                continue

            line_badness = 0 if j == n else trailing ** 3
            total = line_badness + rest
            if total < best:
                best = total

        dp[i] = best

    return int(dp[0])


if __name__ == '__main__':
    assert min_badness(["aaa"], 10) == 0
    assert min_badness(["aa", "aa", "aa"], 20) == 0

    # Sanity: brute-force check on small random inputs.
    import itertools
    import random

    def brute(words, width):
        n = len(words)
        lengths = [len(w) for w in words]
        best = None
        # Choose break positions among the n-1 internal gaps.
        for mask_positions in range(n):
            pass
        # Enumerate all ways to partition into consecutive non-empty lines.
        for cuts_count in range(n):
            for cuts in itertools.combinations(range(1, n), cuts_count):
                bounds = [0] + list(cuts) + [n]
                lines = [(bounds[k], bounds[k + 1]) for k in range(len(bounds) - 1)]
                ok = True
                total = 0
                for idx, (a, b) in enumerate(lines):
                    cnt = b - a
                    used = sum(lengths[a:b]) + (cnt - 1)
                    if used <= width:
                        trailing = width - used
                    elif cnt == 1:
                        trailing = 0
                    else:
                        ok = False
                        break
                    is_last = (idx == len(lines) - 1)
                    total += 0 if is_last else trailing ** 3
                if ok and (best is None or total < best):
                    best = total
        return best

    random.seed(0)
    for _ in range(2000):
        n = random.randint(1, 7)
        width = random.randint(1, 8)
        words = ["a" * random.randint(1, 6) for _ in range(n)]
        got = min_badness(words, width)
        exp = brute(words, width)
        assert got == exp, (words, width, got, exp)
    print("all checks passed")
