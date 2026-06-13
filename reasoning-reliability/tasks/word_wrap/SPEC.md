# Task: line-layout badness minimizer

Implement a single pure function:

```python
def min_badness(words: list[str], width: int) -> int:
    ...
```

## Layout rules

You are laying out `words` (in the given order; you may not reorder them) into lines.
Words placed on the same line are joined by a single space. For a line holding the
words `words[i..j-1]`:

- **used length** = `sum(len(w) for those words) + (number_of_words_on_line - 1)`
- A line is **valid** if `used_length <= width`. **Exception:** a line that holds a
  single word whose length is greater than `width` is also valid (it overflows the
  margin); for such a line treat its used length as exactly `width`.
- **trailing space** of a line = `width - used_length`, clamped to a minimum of 0
  (so an overflowing single-word line has trailing space 0).

Every word must be placed on exactly one line, and line breaks preserve word order.

## Badness

- The **last line** has badness `0` (its trailing space is free).
- Every **other line** has badness `(trailing_space) ** 3`.
- The **total badness** of a layout is the sum of its line badnesses.

## What to return

Return the **minimum total badness achievable over all valid layouts** of `words`
into lines, as an `int`. If the words can be placed at all, a layout always exists.

## Constraints

- `1 <= len(words) <= 400`
- `1 <= width`, and each word length is a positive integer
- Word contents are irrelevant; only their lengths and the single-space joins matter

## Examples

- `min_badness(["aaa"], 10)` -> `0`  (one line, it is the last line)
- `min_badness(["aa","aa","aa"], 20)` -> `0`  (all fit on one line)
- `min_badness(["aaaaaaaaaaaaaaa","aa","aaa"], 10)` -> compute it: the 15-char word
  overflows on its own line (badness 0, treated as used=width), then the remaining
  words; return the minimum total over the valid ways to break what's left.

Return only the function `min_badness` in a single Python file. It will be imported
and called directly.
