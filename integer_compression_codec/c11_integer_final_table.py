#!/usr/bin/env python3
"""integer_compression_codec: old vs final patch, both judges built with sforge's build on one worker, judge_local.py, interleaved. Raw and 0..100, plus the anchor effect isolated: each old run's own sizes and throughput rescored with the exact sizes."""
import glob, json, os, re, statistics as st, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
JOB = sys.argv[1] if len(sys.argv) > 1 else "community11-integer_compression_codec-final"
B = json.load(open(sys.argv[2]))
base = {d["name"]: d for d in B["per_dataset"]}
EXACT = dict(docids=487276069, ts_sec=250000004, ts_ns=246753740, temp=100000004, grid=246847587, zipf=78909904, rand=246848891, sparse=241176008)
new_b = {k: EXACT[k] * 8 / base[k]["n"] for k in EXACT}
def rescore(pd):
    tw = sum(x["weight"] for x in pd); s = 0
    for x in pd:
        if not x.get("roundtrip_ok") or x.get("error"): continue
        s += x["weight"] * min(new_b[x["name"]] / max(x["encoded_bytes"] * 8 / x["n"], 1e-9), 8) * min(x["decode_gbps"] / base[x["name"]]["decode_gbps"], 40)
    return s / tw
print("job status", json.load(open(f"evidence/runs/{JOB}/result/worker.json"))["status"])
R = {}
for f in sorted(glob.glob(f"evidence/runs/{JOB}/result/out/g/*.json")):
    d = json.load(open(f)); m = re.match(r"(old|new)-(\w+)-p(\d)", os.path.basename(f))
    R.setdefault((m.group(2), m.group(1)), []).append((int(m.group(3)), d))
print("| Submission | n | Old raw (= 0..100) | New raw | New 0..100 (raw / 3.2) | Old run's data rescored with exact sizes, raw |")
print("|---|---|---|---|---|---|")
fmt = lambda v: f"{min(v):.2f}-{max(v):.2f}" if max(v) - min(v) >= 0.005 else f"{v[0]:.2f}"
for a in ("top", "flipA", "flipB", "starter", "bad"):
    o = [d["raw_score"] for _, d in sorted(R[a, "old"], key=lambda x: x[0])]; n = [d["raw_score"] for _, d in sorted(R[a, "new"], key=lambda x: x[0])]; s = [d["score_0_100"] for _, d in R[a, "new"]]
    re_ = [rescore(d["result"]["metrics"]["per_dataset"]) for _, d in R[a, "old"]] if a != "bad" else [0.0]
    print(f"| {a} | {len(o)} | {fmt(o)} (mean {st.mean(o):.2f}) | {fmt(n)} (mean {st.mean(n):.2f}) | {fmt(s)} (mean {st.mean(s):.2f}) | {fmt(re_)} |")
    v = [d["valid"] for _, d in R[a, "old"] + R[a, "new"]]; assert all(v), a
    print(f"<!-- {a} old {[round(x,3) for x in o]} new {[round(x,3) for x in n]} -->")
sizes = {a: {tuple(x["encoded_bytes"] for x in d["result"]["metrics"]["per_dataset"]) for sd in ("old", "new") for _, d in R[a, sd]} for a in ("top", "flipA", "flipB", "starter")}
print("distinct size vectors across judges:", {k: len(v) for k, v in sizes.items()})
st0 = R["starter", "new"][0][1]["result"]["metrics"]["per_dataset"]
print("starter new per dataset S_i:", {x["name"]: round(x["score"], 3) for x in st0}, "encoded_bytes == anchor:", all(x["encoded_bytes"] == EXACT[x["name"]] for x in st0))
print("top new/old ratio of mean raw", round(st.mean(d["raw_score"] for _, d in R["top", "new"]) / st.mean(d["raw_score"] for _, d in R["top", "old"]), 3))
print("order: mean raw old", {a: round(st.mean(d["raw_score"] for _, d in R[a, "old"]), 2) for a in ("top", "flipA", "flipB")}, "new", {a: round(st.mean(d["raw_score"] for _, d in R[a, "new"]), 2) for a in ("top", "flipA", "flipB")})
