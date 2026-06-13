"""Measure, per call, whether the tool did its job:
 - self_inspect  -> assumption-surfacing: did the following reasoning name/engage a
   hidden assumption AND act on it (counterexample / revision / qualification)?
 - superposition -> frame-multiplication: did the following reasoning develop a
   genuine second reading / locate itself in the axis AND shift the claim?

Computed signals (markers over the following_reasoning), then per-regime rates.
Also dumps sample triples per regime for human validation of the signals.
"""
import json
import os
import re
import random

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "tool_calls_dataset.jsonl")

FORCED = {"a33b2efff4df", "a546df82ca70"}            # tools every turn
SONNET = {"ab250395fcc9"}                              # sonnet selective
# everything else with calls = haiku selective / build-audit / partials
def regime(run, model):
    if run in SONNET or model == "sonnet":
        return "sonnet-selective"
    if run in FORCED:
        return "haiku-forced-everyturn"
    return "haiku-selective"

ASSUM = re.compile(r"assum|presuppos|taken for granted|implicit|hidden|rests on|"
                   r"treating .{0,20} as|i have been|i'?ve been|i was assum", re.I)
ACT = re.compile(r"counterexample|fails when|fail\b|does not hold|doesn'?t hold|"
                 r"\bbut \b|however|actually|revise|reject|\bwrong\b|break|qualif", re.I)
AXIS = re.compile(r"\bpole\b|\baxis\b|reading|tension|locate|which (am i|side|pole)|"
                  r"the other|alternativ|reframe|two read|diverge|\bvs\b", re.I)
SHIFT = re.compile(r"\bso \b|therefore|this means|this shift|new ground|deepen|"
                   r"revise|reframe|reorganiz|opens|the real question|forces", re.I)

rows = [json.loads(l) for l in open(DATA, encoding="utf-8") if l.strip()]

agg = {}
samples = {}
for r in rows:
    reg = regime(r["run"], r.get("model", "?"))
    fr = r["following_reasoning"] or ""
    responded = len(fr) > 80
    if r["tool"] == "self_inspect":
        named = bool(ASSUM.search(fr))
        acted = bool(ACT.search(fr))
        util = responded and (named or acted)
        key = (reg, "self_inspect")
        agg.setdefault(key, [0, 0, 0])  # n, engaged, util
        agg[key][0] += 1
        agg[key][1] += 1 if responded else 0
        agg[key][2] += 1 if util else 0
    else:
        engaged = bool(AXIS.search(fr))
        shifted = bool(SHIFT.search(fr))
        util = responded and engaged and shifted
        key = (reg, "superposition")
        agg.setdefault(key, [0, 0, 0])
        agg[key][0] += 1
        agg[key][1] += 1 if (responded and engaged) else 0
        agg[key][2] += 1 if util else 0
    samples.setdefault((reg, r["tool"]), []).append(r)

print("=" * 70)
print("UTILITY RATES (signal-based)")
print("=" * 70)
for reg in ("haiku-forced-everyturn", "haiku-selective", "sonnet-selective"):
    for tool in ("self_inspect", "superposition"):
        v = agg.get((reg, tool))
        if not v:
            continue
        n, eng, util = v
        label = "assumption-surfaced+acted" if tool == "self_inspect" else "frame-multiplied+used"
        print("%-26s %-13s  n=%-3d  engaged=%3.0f%%  %s=%3.0f%%"
              % (reg, tool, n, 100 * eng / n, label, 100 * util / n))
    print("-" * 70)

# deterministic sample for validation (seeded by index, not random clock)
print("\n" + "=" * 70)
print("SAMPLES FOR VALIDATION (1 per regime/tool)")
print("=" * 70)
for (reg, tool), rs in sorted(samples.items()):
    r = rs[len(rs) // 2]  # middle one, deterministic
    print("\n### %s | %s | run %s" % (reg, tool, r["run"]))
    print("INPUT   :", (r["input"] or "")[:200])
    print("OUTPUT  :", (r["output"] or "").replace("\n", " ")[:160])
    print("FOLLOWS :", (r["following_reasoning"] or "")[:420])
