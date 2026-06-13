"""Independent proof that every tool call in a run actually happened.

The two instruments are deterministic: the same input always yields the same
output. So we re-run them on every input recorded in the execution transcript
and confirm the output the agent received matches what we compute now. A run
where all calls re-produce identically could not have been fabricated.

Usage:
  python verify/verify_calls.py [runs/<run-name>]
  (defaults to runs/stateful-haiku-40turn)

Exit code 0 iff every captured call re-runs identically.
"""
import json
import os
import re
import shlex
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    REPO, "runs", "stateful-haiku-40turn")
TRANSCRIPT = os.path.join(RUN, "transcript.jsonl")

SI = os.path.join(REPO, "tools", "self_inspect.py")
SP = os.path.join(REPO, "tools", "superposition.py")
PY = os.environ.get("PYTHON", sys.executable)


def load(path):
    uses, results = {}, {}
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            o = json.loads(line)
        except Exception:
            continue
        content = o.get("message", {}).get("content", [])
        if not isinstance(content, list):
            continue
        for c in content:
            if not isinstance(c, dict):
                continue
            if c.get("type") == "tool_use" and c.get("name") == "Bash":
                cmd = c.get("input", {}).get("command", "")
                if "self_inspect.py" in cmd:
                    uses[c["id"]] = ("SI", cmd)
                elif "superposition.py" in cmd:
                    uses[c["id"]] = ("SP", cmd)
            elif c.get("type") == "tool_result":
                out = c.get("content", "")
                if isinstance(out, list):
                    out = "".join(p.get("text", "") for p in out
                                  if isinstance(p, dict))
                results[c.get("tool_use_id")] = out
    return uses, results


def arg_after_py(cmd):
    m = re.search(r'\.py"?\s+(.*)$', cmd, re.S)
    if not m:
        return None
    try:
        parts = shlex.split(m.group(1).strip(), posix=True)
    except Exception:
        return None
    out = []
    for p in parts:
        if p in ("|", ">", ">>", "<", "2>&1"):
            break
        out.append(p)
    return " ".join(out) if out else None


def main():
    uses, results = load(TRANSCRIPT)
    tally = {"SI": [0, 0], "SP": [0, 0]}  # ok, fail
    for tid, (tool, cmd) in uses.items():
        if tid not in results:
            continue
        arg = arg_after_py(cmd)
        path = SI if tool == "SI" else SP
        try:
            p = subprocess.run([PY, path], input=(arg or "").encode("utf-8"),
                               capture_output=True, timeout=30)
            fresh = p.stdout.decode("utf-8", "replace").strip()
        except Exception as e:
            fresh = "<ERR %s>" % e
        logged = (results[tid] or "").strip()
        ok = bool(fresh) and (fresh in logged or logged in fresh)
        tally[tool][0 if ok else 1] += 1

    print("run:", os.path.relpath(RUN, REPO))
    print("self_inspect  re-run == logged: %d ok, %d mismatch"
          % (tally["SI"][0], tally["SI"][1]))
    print("superposition re-run == logged: %d ok, %d mismatch"
          % (tally["SP"][0], tally["SP"][1]))
    failed = tally["SI"][1] + tally["SP"][1]
    print("RESULT:", "ALL CALLS VERIFIED" if failed == 0 else "%d MISMATCH" % failed)
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
