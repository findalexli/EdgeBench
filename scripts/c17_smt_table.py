#!/usr/bin/env python3
"""smt_solver, final code (community17). Real-solver pair, verdict replay summary, controls, ulimit runs, five-file cut, deep shapes.
Run from the repo root."""
import collections, glob, json, os, re
R = "evidence/runs/community17-smt-"
for j in ("checks", "fullpair", "verdicts", "shapes", "defshapes"):
    assert json.load(open(f"{R}{j}/result/worker.json"))["status"] == "exit=0", j
print(open(R + "checks/result/out/tags.txt").readline().strip())
J = R + "fullpair/result/out/"
print("--- real solver pair, order as in summary.txt:", [l.split()[2] for l in open(J + "summary.txt") if l.startswith("sforge real")])
for s in ("old", "new"):
    f = J + f"s/real-{s}.report.json"
    if not os.path.exists(f): print(s, "no report"); continue
    r = json.load(open(f)); o = open(J + f"s/real-{s}.judge_output.txt").read(); bl = r["metrics"].get("by_logic", {})
    print(s, "valid", r["valid"], "score", round(r["score_0_100"], 2), r["summary"].split(", ")[-1], "grade_s", round(r["runtime_seconds"]), "BrokenProcessPool", o.count("BrokenProcessPool"), {k: (v["correct"], v["invalid_model"], v["timeout"], v["error"]) for k, v in bl.items()})
last = {}
for l in open(J + "mem.txt"):
    p = l.split()
    if "oom_kill" not in p: continue
    e = last.setdefault(p[1], dict(t0=int(p[0]), oom=0)); e["t1"] = int(p[0]); e["oom"] = max(e["oom"], int(p[p.index("oom_kill") + 1]))
for k, e in last.items(): print(" container", k, "sampled_s", e["t1"] - e["t0"], "oom_kill", e["oom"])
M = R + "checks/result/out/"
print("--- controls through sforge eval, label side: (score, valid, correct, grade_s) per order")
g = collections.defaultdict(list)
for f in sorted(glob.glob(M + "s/*.report.json")):
    a, p, s = os.path.basename(f)[:-len(".report.json")].rsplit("-", 2); r = json.load(open(f))
    g[(a, s)].append((round(r["score_0_100"], 2), r["valid"], r["summary"].split(", ")[-1], round(r["runtime_seconds"], 1)))
for k in sorted(g): print(k, g[k])
print("--- five-file cut, real solver")
for f in sorted(glob.glob(M + "five/*.json") + glob.glob(M + "g/*.json")):
    r = json.load(open(f)); print(os.path.basename(f), r.get("score_0_100"), r.get("valid"), r.get("summary"), round(r.get("runtime_s") or 0))
print("--- run.sh under a shell limit, reproducer")
for f in sorted(glob.glob(M + "inj/*.log")):
    t = open(f).read(); j = json.loads(t.strip().splitlines()[-1]); m = re.search(r"ValidatorFailure: .*|BrokenProcessPool", t)
    print(os.path.basename(f)[:-4], "stack,as", t.split("\n")[0], t.split("\n")[1], "|", j["valid"], j["summary"], "|", m.group(0)[:70] if m else "")
print("--- deep shapes, final code")
rows = []
for j in ("shapes", "defshapes"):
    for l in open(f"{R}{j}/result/out/sh/results.jsonl"):
        rows.append(json.loads(l))
for r in rows: print({k: (round(v, 1) if isinstance(v, float) else (v[:70] if isinstance(v, str) else v)) for k, v in r.items()})
print("runs", len(rows))
capped = [l.split() for j in ("shapes", "defshapes") for l in open(f"{R}{j}/result/out/summary.txt") if l.startswith("sh ") and "rc=124" in l]
print("capped, no verdict", [(c[2], c[3], c[4]) for c in capped])
kinds = collections.Counter("accepted" if r["verdict"] == "accepted" else r["exc"] + (" (literal parse at limit)" if "unknown symbol" in r["msg"] else " (witness incomplete)" if "missing model" in r["msg"] else "") for r in rows)
print("tally", dict(kinds), "CRASH", sum(r["verdict"] == "CRASH" for r in rows), "total runs", len(rows) + len(capped), "shapes", len({r["shape"] for r in rows}), "max_rss_mib", max(r["rss_mib"] for r in rows))
