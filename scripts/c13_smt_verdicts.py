#!/usr/bin/env python3
"""SMT: old vs new validator on identical solver outputs (community13-smt-verdicts), and the real solver with the five
crashing inputs answered unknown, old then new (community13-smt-preserve). Usage: c13_smt_verdicts.py [runs_dir]"""
import collections, json, sys

RUNS = sys.argv[1] if len(sys.argv) > 1 else "evidence/runs"
base = f"{RUNS}/community13-smt-verdicts/result"
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
base = f"{RUNS}/community13-smt-preserve/result"
assert json.load(open(f"{base}/worker.json"))["status"] == "exit=0"
rep = {s: json.load(open(f"{base}/out/s/real-{s}.report.json")) for s in ("old", "new")}
for s, r in rep.items():
    print("guarded", s, f"{r['score_0_100']:.2f}", r["summary"], f"runtime={r['runtime_seconds']:.0f}", r["metrics"] if len(str(r["metrics"])) < 300 else "")
for logic in rep["old"]["metrics"]["by_logic"]:
    a, b = (rep[s]["metrics"]["by_logic"][logic] for s in ("old", "new"))
    print(" ", logic, *(f"{k}={a[k]}/{b[k]}" for k in ("correct", "timeout", "invalid_model", "unknown", "error")))
