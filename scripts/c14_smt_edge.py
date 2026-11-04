#!/usr/bin/env python3
"""SMT: nesting of the hidden set, validator time against depth, and deep synthetic shapes on the final code
(community14-smt-extent, community14-smt-shapes, community15-smt-chain, community15-smt-defshapes), simulated depth with the
define cache and real models on the deep files run alone (community16-smt-deep), and the old-first pairs. Usage: c14_smt_edge.py [runs_dir]"""
import collections, json, re, sys

RUNS = sys.argv[1] if len(sys.argv) > 1 else "evidence/runs"
FIVE = {"7cf7d9bc1df9f7f0", "85b67deb9ba8a2ab", "8e72757e0b560007", "bc8b317ecdcf7301", "e4bf0f1de993c180"}
for job in ("community14-smt-extent", "community14-smt-shapes"):
    assert json.load(open(f"{RUNS}/{job}/result/worker.json"))["status"] == "exit=0", job
ext = [json.loads(l) for l in open(f"{RUNS}/community14-smt-extent/result/out/extent.jsonl")]
ext.sort(key=lambda r: -r["paren_depth"])
print("inputs", len(ext), "by paren depth, deepest first:")
for r in ext[:14]:
    print(" ", r["key"], "depth", r["paren_depth"], "size", r["size"], "lets", r["lets"], "ites", r["ites"], "expected", r["expected"], "FIVE" if r["key"].split("/")[1][:16] in FIVE else "")
five = [r for r in ext if r["key"].split("/")[1][:16] in FIVE]
print("five: depth", min(r["paren_depth"] for r in five), "-", max(r["paren_depth"] for r in five))
print("other files at or above the five's shallowest depth:", [r["key"] for r in ext if r["paren_depth"] >= min(x["paren_depth"] for x in five) and r not in five])
print("deepest other file:", next(r["paren_depth"] for r in ext if r not in five))
for line in open(f"{RUNS}/community14-smt-extent/result/out/sh/results.jsonl"):
    r = json.loads(line)
    print(" ladder", r["code"], r["shape"], r["depth"], r["verdict"], r.get("exc", ""), r["secs"], "s", r["rss_mib"], "MiB")
got = {}
for line in open(f"{RUNS}/community14-smt-shapes/result/out/sh/results.jsonl"):
    r = json.loads(line); got[(r["shape"], r["depth"])] = r
counts = collections.Counter(); caps = []
for line in open(f"{RUNS}/community14-smt-shapes/result/out/summary.txt"):
    m = re.match(r"sh /e/final.py (\w+) (\d+) cap=\d+ rc=(\d+)", line)
    if m:
        k = (m[1], int(m[2]))
        if k in got:
            counts[got[k]["verdict"]] += 1
        else:
            assert m[3] == "124", line
            counts["cap"] += 1; caps.append(k)
print("final code, 13 shapes x 3 depths:", dict(counts), "peak RSS MiB", max(r["rss_mib"] for r in got.values()), "slowest verdict", max(r["secs"] for r in got.values()))
print("no verdict within 170 s:", caps)
print("exceptions", collections.Counter(r.get("exc") for r in got.values()))
runs = 0; verdicts = collections.Counter(); peak = 0
for job in ("community15-smt-chain", "community15-smt-defshapes"):
    assert json.load(open(f"{RUNS}/{job}/result/worker.json"))["status"] == "exit=0", job
    for line in open(f"{RUNS}/{job}/result/out/sh/results.jsonl"):
        r = json.loads(line); runs += 1; verdicts[r["verdict"]] += 1; peak = max(peak, r["rss_mib"])
        print(" define family", r["shape"], r["depth"], r["verdict"], r.get("exc", ""), r["secs"], "s", r["rss_mib"], "MiB")
print("define family runs", runs, dict(verdicts), "peak RSS MiB", peak)
print("all deep-shape runs", runs + sum(counts.values()), "crashes", verdicts["CRASH"] + counts["CRASH"], "no verdict", counts["cap"])
deep = f"{RUNS}/community16-smt-deep/result"
assert json.load(open(f"{deep}/worker.json"))["status"] == "exit=0"
sim = sorted((json.loads(l) for l in open(f"{deep}/out/sim.jsonl")), key=lambda r: -r["sim_frames"])
print("simulated frames, no short-circuit, deepest first (the deepest captured witness needs 600,000-800,000 on 7cf7d9bc):")
for r in sim[:15]:
    print(" ", r["key"], r["expected"], r["sim_frames"])
print("sat files above 1,000,000:", sum(r["expected"] == "sat" and r["sim_frames"] > 1000000 for r in sim))
print("deep files, solver alone at 7 GiB, 75 s cap:")
for line in open(f"{deep}/out/capture.jsonl"):
    r = json.loads(line); print(" ", r["key"], r["answer"], r["secs"])
for line in open(f"{deep}/out/check.jsonl"):
    r = json.loads(line); print(" ", r["key"], "old", r["old"], r["old_s"], "new", r["new"], r["new_s"])
for job in ("community13-smt-oldfirst", "community14-smt-oldfirst"):
    w = json.load(open(f"{RUNS}/{job}/result/worker.json")); r = json.load(open(f"{RUNS}/{job}/result/out/s/real-old.report.json"))
    t = int(re.search(r"sforge real old rc=0 t=(\d+)", open(f"{RUNS}/{job}/result/out/summary.txt").read())[1])
    print(job, "old", r["score_0_100"], r["summary"], round(r["runtime_seconds"]), "s; new unfinished", w["elapsed_s"] - t, "s in, status", w["status"])
