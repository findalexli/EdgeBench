#!/usr/bin/env python3
"""smt_solver split: validator-only branch (community18-smt-validator-pair1, -pair2, -checks) and status-only branch (community18-smt-status-checks2). Run from the repo root."""
import collections, glob, json, os
R = "evidence/runs/community18-smt-"
def st(j): return json.load(open(f"{R}{j}/result/worker.json"))["status"]
for j in ("validator-pair1", "validator-pair2"):
    J = f"{R}{j}/result/out/"; print("---", j, st(j), open(J + "tags.txt").read().split("key ")[-1].strip(), "order", [l.split()[2] for l in open(J + "summary.txt") if l.startswith("sforge real")])
    for s in ("old", "new"):
        f = J + f"s/real-{s}.report.json"
        if not os.path.exists(f): print(s, "no report"); continue
        r = json.load(open(f)); o = open(J + f"s/real-{s}.judge_output.txt").read(); bl = r["metrics"].get("by_logic", {})
        print(s, "valid", r["valid"], "score", round(r["score_0_100"], 2), r["summary"].split(", ")[-1], "grade_s", round(r["runtime_seconds"]), "BrokenProcessPool", o.count("BrokenProcessPool"), {k: (v["correct"], v["invalid_model"], v["timeout"], v["error"]) for k, v in bl.items()})
for j in ("validator-checks", "status-checks2"):
    M = f"{R}{j}/result/out/"; print("---", j, st(j), open(M + "tags.txt").readline().strip() if os.path.exists(M + "tags.txt") else "")
    g = collections.defaultdict(list)
    for f in sorted(glob.glob(M + "s/*.report.json")):
        a, p, s = os.path.basename(f)[:-len(".report.json")].rsplit("-", 2); r = json.load(open(f)); o = open(f[:-len("report.json")] + "judge_output.txt").read()
        g[(a, s)].append((round(r["score_0_100"], 2) if r["score_0_100"] is not None else None, r["valid"], r["summary"].split(", ")[-1][:60], "BPP" if "BrokenProcessPool" in o else ""))
    for k in sorted(g): print(k, g[k])
