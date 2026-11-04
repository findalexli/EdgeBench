#!/usr/bin/env python3
"""SMT: old vs final validator on identical solver outputs (community17-smt-verdicts), and capture against community13's solver run. Usage: c17_smt_verdicts.py [runs_dir]"""
import collections, json, sys

RUNS = sys.argv[1] if len(sys.argv) > 1 else "evidence/runs"
base = f"{RUNS}/community17-smt-verdicts/result"
assert json.load(open(f"{base}/worker.json"))["status"] == "exit=0"
cap = [json.loads(l) for l in open(f"{base}/out/capture.jsonl")]
chk = [json.loads(l) for l in open(f"{base}/out/check.jsonl")]
print("inputs", len(cap), "with model", sum(r["has_witness"] for r in cap), "checked", len(chk))
pairs = collections.Counter((r["old"].split()[0], r["new"].split()[0]) for r in chk)
for k, v in sorted(pairs.items()):
    print(" ", k, v)
print("identical verdict text", sum(r["old"] == r["new"] for r in chk))
print("differ:")
for r in chk:
    if r["old"] != r["new"]:
        print(" ", r["key"], r["old"], "->", r["new"], f"old_s={r['old_s']} new_s={r['new_s']}")
reasons = collections.Counter((r["key"].split("/")[0], r["new"].split(" ", 2)[1], " ".join(r["new"].split()[2:4])) for r in chk if r["new"].startswith("rejected"))
for k, v in reasons.most_common():
    print(" rejected by both", k, v)
print("slowest new_s", max(r["new_s"] for r in chk), "total old_s", round(sum(r["old_s"] for r in chk)), "total new_s", round(sum(r["new_s"] for r in chk)))
