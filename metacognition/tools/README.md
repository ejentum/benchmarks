# tools

The exact instruments used by the runs in this repo. Both are single-file,
zero-dependency, stdlib-only Python. No LLM, no network, no key. Deterministic:
the same input always returns the same output.

## `self_inspect.py`

A thought in, one *metathought* out: a short question that turns attention onto
an unstated assumption. Selection is a transparent heuristic over an open table
inlined in the file. Always returns a question.

```sh
python self_inspect.py "I am committing to this architecture and treating it as fixed"
# -> [{"label": "commitment", "metathought": "What is fixed?"}]
```

Canonical source, tests, and the REST/MCP surfaces: https://github.com/ejentum/self-inspect-mcp
This copy is the generated single-file build (`dist/self_inspect.py`), held
byte-identical to the published JS engine by a cross-language parity test in that repo.

## `superposition.py`

A `{"task","description","wants"}` in, a two-pole tension map out: two readings
of what you are doing and a question about which is the real measure. A forcing
function for divergence; it sharpens the tension rather than resolving it.

```sh
python superposition.py '{"task":"measuring progress","description":"I keep shipping commits","wants":"to know if I am actually closer to done"}'
```

## Why they are vendored here

So a run is reproducible from this repo alone. `verify/verify_calls.py` re-runs
these exact files against the recorded inputs in a run's transcript and confirms
the outputs match. Updating a tool upstream does not retroactively change a run's
proof, because the proof uses the copy committed alongside the data.
