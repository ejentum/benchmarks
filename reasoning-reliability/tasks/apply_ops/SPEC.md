# Task: apply text operations

Implement a single pure function:

```python
def apply_ops(text: str, ops: list[tuple[str, str]]) -> str:
    ...
```

`ops` is an ordered list of `(find, replace)` pairs. Every `find` is a non-empty
string; `replace` may be any string (including empty). Apply the operations to
`text` and return the resulting string.

## Exact semantics

Process `text` in a **single left-to-right pass over the ORIGINAL input**, with a
cursor starting at position 0:

1. At the current cursor position `i`, consider the ops **in their given list
   order**. The **first** op whose `find` exactly matches the original text
   starting at `i` (i.e. `text[i : i+len(find)] == find`) is the one that fires.
2. When an op fires, append its `replace` to the output, and advance the cursor
   by `len(find)` (past the matched span in the **original** text).
3. If no op matches at position `i`, append the single original character
   `text[i]` to the output and advance the cursor by 1.
4. Repeat until the cursor reaches the end of `text`.

Crucially: matching is always done against the **original** `text`. Text emitted
by a `replace` is part of the output only; it is **never re-scanned** and can
never trigger further matches. Op priority at a position is **list order**, not
longest-match.

## Examples

- `apply_ops("a", [("a","b"), ("b","c")])` -> `"b"`
  (At position 0, the first op matches `"a"` and emits `"b"`. The emitted `"b"`
  is output only and is not re-scanned, so the second op never fires.)
- `apply_ops("ab", [("a","x"), ("ab","y")])` -> `"xb"`
  (At position 0, list order means the first op `("a","x")` fires, not the
  longer `("ab","y")`. Emit `"x"`, advance 1; then `"b"` has no match.)
- `apply_ops("cat", [("cat","dog"), ("dog","bird")])` -> `"dog"`
- `apply_ops("hello", [])` -> `"hello"`

Return only the function `apply_ops` in a single Python file. It will be imported
and called directly.
