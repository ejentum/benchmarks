"""Compute the tools-on vs no-tools delta over the two run journals.

Metrics (model-generated text only; tool outputs are excluded so the comparison
is the model's own reasoning in both arms):
  - back-half / front-half content length  (the "content thinning" signal)
  - next-question length, back / front      (the forward-question collapse)
  - turns hitting the introspective bind, and the first such turn
  - explicit self-reference density (reported but treated as confounded)

Usage:  python delta.py
"""
import json
import os
import re

REPO = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.join(REPO, "runs", "stateful-haiku-40turn", "journal.jsonl")
CTRL = os.path.join(REPO, "runs", "control-haiku-40turn-notools", "journal.jsonl")

BIND = re.compile(
    r"hidden|self-deception|deceiv|cannot (see|know|evaluat|escap|trust)|trap|"
    r"opacity|opaque|colon|recurs|regress|spiral|not transparen|fails? to see|"
    r"sophisticat", re.I)
SELFREF = re.compile(r"turn \d+|earlier turn|as I (established|noted|said)", re.I)


def load(path, body_fields):
    rows = []
    raw = open(path, "rb").read().decode("utf-8", "replace")
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            o = json.loads(line)
        except Exception:
            continue
        rows.append({
            "turn": o.get("turn"),
            "body": " ".join(str(o.get(f, "")) for f in body_fields),
            "nq": str(o.get("next_question", "")),
            "all": " ".join(str(v) for v in o.values()),
        })
    return rows


def stats(rows, name):
    body = [len(r["body"]) for r in rows]
    nq = [len(r["nq"]) for r in rows]
    fh, bh = sum(body[:20]) / 20, sum(body[20:]) / 20
    nqf, nqb = sum(nq[:20]) / 20, sum(nq[20:]) / 20
    bind = [r["turn"] for r in rows if BIND.search(r["all"])]
    sref = [r["turn"] for r in rows if SELFREF.search(r["all"])]
    print("--- %s (n=%d) ---" % (name, len(rows)))
    print("  body chars/turn: front=%.0f back=%.0f  back/front=%.2f" % (fh, bh, bh / fh))
    print("  next_question chars/turn: front=%.0f back=%.0f  back/front=%.2f" % (nqf, nqb, nqb / nqf))
    print("  bind markers: %d/40, first at turn %s" % (len(bind), bind[0] if bind else None))
    print("  self-reference (confounded): %d/40" % len(sref))
    return {"thin": bh / fh, "nq": nqb / nqf, "bind": len(bind), "first": bind[0] if bind else None}


# tools-on: model text = claim + reframe + answer + insight (map/metathought are tool outputs)
# control:  model text = claim + development + insight
t = stats(load(TOOLS, ["claim", "reframe", "answer", "insight"]), "TOOLS-ON")
print()
c = stats(load(CTRL, ["claim", "development", "insight"]), "CONTROL (no tools)")
print("\n=== DELTA ===")
print("  content thinning (back/front):  tools=%.2f  control=%.2f" % (t["thin"], c["thin"]))
print("  next-question collapse:         tools=%.2f  control=%.2f" % (t["nq"], c["nq"]))
print("  introspective-bind turns:       tools=%d/40  control=%d/40" % (t["bind"], c["bind"]))
print("  first bind appears:             tools=turn %s  control=turn %s" % (t["first"], c["first"]))
