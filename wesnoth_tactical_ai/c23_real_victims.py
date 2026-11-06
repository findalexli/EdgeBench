#!/usr/bin/env python3
"""Real-victim checks. Wesnoth: Qwen3.8's public archive, old vs new. Graph and Warehouse: public histories and Sonnet runs.
Usage: c23_real_victims.py <wesnoth job>/result/out <hf dir> <sonnet dir>"""
import collections, glob, json, os, re, sys

out, hf, sn = sys.argv[1:4]
g = collections.defaultdict(list)
for f in sorted(glob.glob(f"{out}/s/*.log")):
    m = re.match(r"qwen38-(\d+)-(old|new)", os.path.basename(f))
    t = open(f).read()
    d = json.loads(re.search(r"^\{.*\}", t, re.S | re.M).group(0))
    g[m.group(2)].append((int(m.group(1)), d["score_0_100"], d["metrics"]["cases_passed"], round(d["runtime_seconds"]), d["valid"], d["timed_out"]))
for s in ("old", "new"):
    r = sorted(g[s])
    sc = [x[1] for x in r]
    print("wesnoth qwen38", s, "n", len(r), "scores", sc, "mean", round(sum(sc) / len(sc), 2) if sc else None, "wins", [x[2] for x in r], "runtime_s", [x[3] for x in r], "valid", {x[4] for x in r}, "timed_out", {x[5] for x in r})


def hist(p):
    return [x for x in json.load(open(p)).get("entries", []) if x.get("type", "submission") == "submission"]


gh = [p for p in glob.glob(f"{hf}/**/run_history.json", recursive=True) if "graph_node" in p]
tot = q = z = 0
for p in gh:
    for x in hist(p):
        tot += 1
        v = re.search(r"overall_score=([\d.]+)", str(x.get("summary")))
        if v:
            q += 1
            z += float(v.group(1)) == 0
print("graph public: histories", len(gh), "entries", tot, "with overall_score", q, "overall==0", z)
wh = [p for p in glob.glob(f"{hf}/**/run_history.json", recursive=True) if "warehouse" in p]
print("warehouse public: histories", len(wh), "entries", sum(len(hist(p)) for p in wh))
tle = []
for f in glob.glob(f"{hf}/**/warehouse_forklift_routing/submissions/*/report.json", recursive=True):
    d = json.load(open(f))
    names = [x["name"] for x in d.get("test_details", d.get("details", []))]
    n = sum("TLE" in x for x in names)
    if n:
        tle.append((f.split("/")[-2], n, sum("_RE" in x for x in names), sum("_WA" in x for x in names), round(d.get("runtime_seconds") or 0)))
print("warehouse Kimi reports with TLE (round, TLE, RE, WA, runtime_s)", tle)
for t, pat in (("graph_node_classification", r"solution/solution\.py"), ("warehouse_forklift_routing", r"solution\.py")):
    for r in sorted(glob.glob(f"{sn}/{t}-*")):
        print(os.path.basename(r), open(f"{r}/status.txt").read().strip() if os.path.exists(f"{r}/status.txt") else "no-status")
