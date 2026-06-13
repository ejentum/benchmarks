"""Extract every real tool call across all metacognition runs, each paired with
the agent's reasoning that immediately follows it (its response to the tool).
This is the dataset for measuring assumption-surfacing (self-inspect) and
frame-multiplication (superposition). Deterministic; no judgment here.

Output: analysis/tool_calls_dataset.jsonl  (one row per call)
  {run, model, tool, call_index, input, output, following_reasoning}
"""
import json
import glob
import os
import re

SUB = ("C:/Users/frank/.claude/projects/c--Users-frank-Desktop-ejentum/"
       "4ee348c1-22b3-4375-8fa1-0a0d3b6dfe46/subagents")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tool_calls_dataset.jsonl")

SEED_MARK = ("examines its own thinking", "examine its own thinking",
             "examining its own thinking")


def ordered_events(path):
    """Flatten transcript into ordered (kind, payload) with tool_results resolved."""
    results = {}
    raw = []
    lines = list(open(path, encoding="utf-8", errors="replace"))
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            o = json.loads(line)
        except Exception:
            continue
        for c in (o.get("message", {}).get("content", []) or []):
            if isinstance(c, dict) and c.get("type") == "tool_result":
                out = c.get("content", "")
                if isinstance(out, list):
                    out = "".join(p.get("text", "") for p in out if isinstance(p, dict))
                results[c.get("tool_use_id")] = out
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            o = json.loads(line)
        except Exception:
            continue
        for c in (o.get("message", {}).get("content", []) or []):
            if not isinstance(c, dict):
                continue
            if c.get("type") == "text" and c.get("text", "").strip():
                raw.append(("TEXT", c["text"]))
            elif c.get("type") == "tool_use" and c.get("name") == "Bash":
                cmd = c.get("input", {}).get("command", "")
                tool = None
                if "self_inspect.py" in cmd:
                    tool = "self_inspect"
                elif "superposition" in cmd:
                    tool = "superposition"
                if tool:
                    raw.append(("CALL", {"tool": tool, "cmd": cmd,
                                          "out": results.get(c.get("id"), "")}))
    return raw


def arg_after_py(cmd):
    m = re.search(r"\.py[\"'\s]+(.*)$", cmd, re.S)
    return m.group(1).strip()[:600] if m else cmd[:600]


def model_of(run_id):
    mf = os.path.join(SUB, "agent-%s.meta.json" % run_id)
    if os.path.exists(mf):
        try:
            return json.load(open(mf)).get("agentType", "?")
        except Exception:
            pass
    return "?"


rows = []
for f in glob.glob(os.path.join(SUB, "agent-*.jsonl")):
    if ".meta" in f:
        continue
    blob = open(f, encoding="utf-8", errors="replace").read()
    if not any(m in blob for m in SEED_MARK):
        continue
    if "self_inspect.py" not in blob and "superposition" not in blob:
        continue
    run_id = os.path.basename(f)[len("agent-"):-len(".jsonl")][:12]
    model = model_of(os.path.basename(f)[len("agent-"):-len(".jsonl")])
    ev = ordered_events(f)
    idx = 0
    for i, (kind, payload) in enumerate(ev):
        if kind != "CALL":
            continue
        idx += 1
        # following reasoning = the next TEXT block(s) until the next CALL
        following = []
        for k2, p2 in ev[i + 1:]:
            if k2 == "CALL":
                break
            if k2 == "TEXT":
                following.append(p2)
            if sum(len(x) for x in following) > 900:
                break
        rows.append({
            "run": run_id,
            "model": model,
            "tool": payload["tool"],
            "call_index": idx,
            "input": arg_after_py(payload["cmd"]),
            "output": (payload["out"] or "").strip()[:300],
            "following_reasoning": " ".join(following).strip()[:900],
        })

with open(OUT, "w", encoding="utf-8") as fh:
    for r in rows:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")

# summary
from collections import Counter
by_run = Counter((r["run"], r["tool"]) for r in rows)
print("total call rows:", len(rows))
runs = sorted(set(r["run"] for r in rows))
print("%-14s %8s %8s" % ("run", "selfinsp", "superpos"))
for run in runs:
    si = by_run.get((run, "self_inspect"), 0)
    sp = by_run.get((run, "superposition"), 0)
    print("%-14s %8d %8d" % (run, si, sp))
print("wrote:", OUT)
