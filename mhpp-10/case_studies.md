# Case Studies: Three Tasks Where the Harness Fingerprint Is Visible

Companion to `REPORT.md`. Pass rate was identical across B/D/A on all three tasks. The reasoning fingerprint is in the code itself.

---

## Case 1: `mhpp_130` (count_subs)

### Problem

Given a string `s` of lowercase letters and integer `count`, return the number of contiguous substrings of `s` in which every distinct letter that appears in the substring appears exactly `count` times.

### B (raw baseline)

```python
from typing import List

def count_subs(s: str, count: int) -> int:
    n = len(s)
    result = 0
    for i in range(n):
        freq = {}
        for j in range(i, n):
            freq[s[j]] = freq.get(s[j], 0) + 1
            if all(v == count for v in freq.values()):
                result += 1
    return result
```

11 lines. Brute force O(n²): outer loop on starting index, inner loop extending the end, recompute the freq table incrementally, check the all-equal condition. No invariant stated. No pruning. No boundary check.

### D (dynamic code)

```python
from typing import List

def count_subs(s: str, count: int) -> int:
    n = len(s)
    if count <= 0 or n == 0:
        return 0
    result = 0
    for i in range(n):
        freq = {}
        over = False
        for j in range(i, n):
            c = s[j]
            freq[c] = freq.get(c, 0) + 1
            if freq[c] > count:
                over = True
                break
            if all(v == count for v in freq.values()):
                result += 1
    return result
```

Same O(n²) algorithmic class as B, but with:

1. Boundary guard `if count <= 0 or n == 0: return 0`.
2. Correctness-preserving prune: `if freq[c] > count: break`. Once any character exceeds count, no extension of this substring can ever satisfy the constraint, so the inner loop terminates early.

The prune is the meaningful contribution. It is not defensiveness; it is an algorithmic insight. B's solution does not make this observation.

### A (adaptive code)

```python
from typing import List


def count_subs(s: str, count: int) -> int:
    n = len(s)
    if n == 0 or count <= 0:
        return 0
    result = 0
    # A valid substring with k distinct letters each appearing exactly `count` times
    # has length k * count. k can be 1..26.
    for k in range(1, 27):
        L = k * count
        if L > n:
            break
        freq = {}
        # initialize first window
        for i in range(L):
            c = s[i]
            freq[c] = freq.get(c, 0) + 1
        # check whether all distinct letters have frequency exactly == count
        # and number of distinct letters equals k
        def valid(f):
            if len(f) != k:
                return False
            for v in f.values():
                if v != count:
                    return False
            return True
        if valid(freq):
            result += 1
        # slide
        for i in range(L, n):
            add_c = s[i]
            rem_c = s[i - L]
            freq[add_c] = freq.get(add_c, 0) + 1
            freq[rem_c] -= 1
            if freq[rem_c] == 0:
                del freq[rem_c]
            if valid(freq):
                result += 1
    return result
```

39 lines. Completely different algorithmic class. The opening comment states a mathematical invariant:

> A valid substring with k distinct letters each appearing exactly count times has length k * count. k can be 1..26.

From this invariant the algorithm follows: enumerate k from 1 to 26, slide a fixed-size window of length k * count, count valid windows. Complexity is O(26n) instead of O(n²).

The interpretation: A stated the invariant first; B and D did not. Stating the invariant changed the algorithmic class. On the small test inputs, all three pass. On a 10,000-character input, A is approximately 400 times faster.

---

## Case 2: `mhpp_132` (minimum_coins)

### Problem

Fruit market with prices in `prices` (1-indexed). Buying the i-th fruit costs `prices[i-1]` and grants the next i fruits for free. Free fruits can themselves be bought to extend the free range. Return the minimum cost to acquire all fruits.

### B (raw baseline)

```python
from typing import List

def minimum_coins(prices: List[int]) -> int:
    n = len(prices)
    if n == 0:
        return 0
    # dp[i] = minimum coins to acquire fruits 1..i (1-indexed)
    INF = float('inf')
    dp = [INF] * (n + 1)
    dp[0] = 0
    for i in range(1, n + 1):
        # Buy fruit i: pay prices[i-1], then fruits i+1 .. i+i are free
        cost = dp[i-1] + prices[i-1]
        # After buying fruit i, we have fruits 1..min(n, 2i) acquired
        reach = min(n, 2 * i)
        for j in range(i, reach + 1):
            if cost < dp[j]:
                dp[j] = cost
    return dp[n]
```

Forward dynamic program. `dp[i]` represents the minimum cost to acquire fruits 1..i. The state is updated by "buy fruit i, propagate the cost to all positions that this purchase reaches." Correct on the test inputs, but the state semantics are subtly muddled: an entry `dp[j]` does not record a single coherent plan; it records the cheapest cost of any plan that reaches at least position j.

### D (dynamic code)

```python
from typing import List


def minimum_coins(prices: List[int]) -> int:
    n = len(prices)
    if n == 0:
        return 0
    # dp[i] = minimum coins to acquire all fruits from 1-indexed position i..n
    # dp[n+1] = 0 (nothing left)
    # Buying fruit i covers itself + next i fruits for free (i.e., positions i+1..2i).
    # Next decision starts at some j in [i+1, 2i+1]; j > n means done.
    dp = [0] * (n + 2)
    for i in range(n, 0, -1):
        best = float('inf')
        upper = min(2 * i + 1, n + 1)
        for j in range(i + 1, upper + 1):
            if dp[j] < best:
                best = dp[j]
        if best == float('inf'):
            best = 0
        dp[i] = prices[i - 1] + best
    return dp[1]
```

Backward dynamic program. `dp[i]` is now "minimum cost to acquire ALL fruits from position i to n," with the base case `dp[n+1] = 0` meaning "no fruits remain." The recursion is clean: must buy fruit i, then pick the cheapest next-buy position in `[i+1, 2i+1]`.

Every cell of the DP table has an unambiguous meaning. The state semantics support invariant-based reasoning.

### A (adaptive code)

```python
from typing import List

def minimum_coins(prices: List[int]) -> int:
    n = len(prices)
    if n == 0:
        return 0
    # dp[i] = minimum coins to acquire all fruits from 1-indexed position i to n
    # dp has size n+2 to safely index dp[n+1]
    INF = float('inf')
    dp = [INF] * (n + 2)
    dp[n + 1] = 0
    # Also any index > n means "nothing left to acquire"
    for i in range(n, 0, -1):
        # We must acquire fruit i. Buy it: pay prices[i-1].
        # This grants free fruits at positions i+1 .. i+i = 2i.
        # Next decision point: choose some j in [i+1, 2i+1] as the next fruit to BUY
        # (j = 2i+1 means accept all free fruits and continue from there).
        cost = prices[i - 1]
        best = INF
        upper = min(2 * i + 1, n + 1)
        for j in range(i + 1, upper + 1):
            if dp[j] < best:
                best = dp[j]
        if best == INF:
            best = 0
        dp[i] = cost + best
    return dp[1]
```

Same backward dynamic program as D, with two additional features:

1. Explicit `INF` initialization for `dp[1..n]` versus D's lazier `[0] * (n+2)` with implicit reliance on `n+1` being the only non-INF entry. A's framing makes the unreachable-state semantics explicit.
2. The comment block explicitly states the algorithmic justification: "must acquire fruit i", "buying it grants free fruits", "next decision point j in [i+1, 2i+1]". The invariants are written down rather than implicit.

B reached a correct answer by procedural thinking. D and A reached it by mathematical induction over remaining work. The backward DP framework composes cleanly under specification drift; the forward framework does not.

---

## Case 3: `mhpp_136` (count_full_weeks)

### Problem

Given a year and month, return the number of complete Monday-to-Sunday weeks that fall entirely within that month.

### B (raw baseline)

```python
import calendar

def count_full_weeks(year: int, month: int) -> int:
    """
    Return the number of complete weeks (Monday-Sunday) in the given month.
    """
    cal = calendar.Calendar(firstweekday=0)  # Monday = 0
    weeks = cal.monthdatescalendar(year, month)
    full_weeks = 0
    for week in weeks:
        if all(d.month == month for d in week):
            full_weeks += 1
    return full_weeks
```

Delegates to the standard library. `calendar.Calendar.monthdatescalendar` returns the month's week grid, including days from neighboring months that pad incomplete weeks at the edges. Filter for weeks where every day belongs to the target month. This is a high-level, library-driven solution. It works.

### D (dynamic code)

```python
import calendar
from datetime import date, timedelta

def count_full_weeks(year: int, month: int) -> int:
    days_in_month = calendar.monthrange(year, month)[1]
    first = date(year, month, 1)
    # weekday(): Monday=0 ... Sunday=6
    # Days until first Monday
    offset = (7 - first.weekday()) % 7
    first_monday_day = 1 + offset
    # Complete Mon-Sun weeks fit if first_monday_day + 6 <= days_in_month
    count = 0
    start = first_monday_day
    while start + 6 <= days_in_month:
        count += 1
        start += 7
    return count
```

Drops to primitives. Compute the day-of-month of the first Monday, then iterate while a complete Mon-Sun week still fits within the month's days. The reasoning is broken down into named steps with inline comments.

### A (adaptive code)

```python
import calendar

def count_full_weeks(year: int, month: int) -> int:
    first_weekday, days_in_month = calendar.monthrange(year, month)
    # first_weekday: 0=Monday ... 6=Sunday
    # Days until first Monday (inclusive of day 1 if it's Monday)
    offset_to_first_monday = (7 - first_weekday) % 7
    first_monday_day = 1 + offset_to_first_monday
    # Count complete Mon-Sun weeks starting from first_monday_day
    remaining_days = days_in_month - first_monday_day + 1
    if remaining_days < 0:
        return 0
    return remaining_days // 7
```

Same setup as D, but derives the answer in closed form: `remaining_days // 7`. No loop. Adds a defensive `if remaining_days < 0: return 0` guard for the mathematically possible (but physically impossible for any real Gregorian month) case where the first Monday lands past the end of the month.

The progression B to D to A maps to three levels of abstraction:

* B: trust the library.
* D: iterate from primitives.
* A: derive the closed form from primitives.

All three pass the test. A reveals the mathematical structure of the problem.

---

## What ties the three together

Across all three case studies, the same pattern recurs: A states the invariant or mathematical structure before writing code, and the code that follows is shaped by the stated invariant. B writes code that happens to be correct without stating why. D sits between, often matching A's framework but without the same depth of invariant statement.

This is the engineered-versus-ad-hoc distinction described in `REPORT.md` Section 5. On a saturated benchmark with a strong model, both produce passing answers. They differ in algorithmic class, in robustness to specification drift, and in auditability under code review.
