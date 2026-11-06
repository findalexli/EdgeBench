#!/usr/bin/env python3
"""integer_compression_codec: what each fix option does to every archived real report, recomputed exactly from the report's own per-dataset encoded_bytes and decode_gbps.
Old anchors and judge formula from runner_judge.py compute_total_score; the recomputation must equal each report's stored score.
usage: c11_integer_archive_options.py <upstream baseline_results.json>"""
import glob, hashlib, itertools, json, os, sys
T = "integer_compression_codec"; ROOT = "evidence/runs/"
base = {d["name"]: d for d in json.load(open(sys.argv[1]))["per_dataset"]}
EXACT = dict(docids=487276069, ts_sec=250000004, ts_ns=246753740, temp=100000004, grid=246847587, zipf=78909904, rand=246848891, sparse=241176008)
old_b = {k: v["bpi"] for k, v in base.items()}
new_b = {k: EXACT[k] * 8 / base[k]["n"] for k in EXACT}
def score(pd, a):
    tw = sum(x["weight"] for x in pd); s = 0; sat = 0
    for x in pd:
        if not x.get("roundtrip_ok") or x.get("error"): continue
        bpi = x["encoded_bytes"] * 8 / max(x["n"], 1); c = a[x["name"]] / max(bpi, 1e-9); sat += c >= 8
        s += x["weight"] * min(c, 8) * min(x["decode_gbps"] / base[x["name"]]["decode_gbps"], 40)
    return s / tw, sat
rows = []; mismatch = 0
for a in sorted(glob.glob(ROOT + f"claude-opus-{T}*/result/out/sforge-logs/runs/*/{T}/submissions/*/submission.tar.gz")):
    rp = a.replace("submission.tar.gz", "report.json")
    if not os.path.exists(rp): continue
    d = json.load(open(rp)); m = d.get("metrics") or {}
    if m.get("status") != "ok": continue
    so, sat_o = score(m["per_dataset"], old_b); sn, sat_n = score(m["per_dataset"], new_b)
    if abs(so - d["score"]) > 1e-6: mismatch += 1
    rows.append(dict(sha=hashlib.sha256(open(a, "rb").read()).hexdigest()[:10], run=a.split("/")[2][-3:], sub=a.split("/")[-2], stored=d["score"], old=so, new=sn, sat_o=sat_o, sat_n=sat_n, sizes=tuple(x["encoded_bytes"] for x in m["per_dataset"])))
print(f"reports n={len(rows)}, recomputed old score differs from the stored score on {mismatch} reports")
files = {}
for r in rows: files.setdefault(r["sha"], []).append(r)
print(f"distinct files n={len(files)}")
print("exact starter bpi:", {k: round(v, 6) for k, v in new_b.items()})
top = [r for r in rows if r["new"] >= 100]
print(f"reports with corrected raw >= 100: {len(top)} of {len(rows)}; files {len({r['sha'] for r in top})} of {len(files)}")
reals = [r for r in rows if r["old"] > 1]
print(f"reports other than the starter: {len(reals)}; of those clipping at 100 on the 0..100 scale with corrected sizes: {sum(r['new'] >= 100 for r in reals)}")
ratio = [r["new"] / r["old"] for r in reals]
print(f"new raw / old raw on those reports: min {min(ratio):.3f} max {max(ratio):.3f}, so no constant factor")
print("\nper file means (n reports), old raw (= current 0..100 score); corrected raw; A = corrected, 0..100 clipped; B = corrected, 0..320; C = corrected, 1..320; datasets at the 8x size cap old -> new")
tab = []
for sha, rs in files.items():
    o = sum(r["old"] for r in rs) / len(rs); n = sum(r["new"] for r in rs) / len(rs)
    tab.append((o, n, rs[0]["run"], rs[0]["sub"], sha, len(rs), rs[0]["sat_o"], rs[0]["sat_n"]))
tab.sort(reverse=True)
for o, n, run, sub, sha, c, so, sn in tab:
    print(f"{sha} {run} {sub:9s} n={c:2d} old {o:7.3f} corrected {n:8.3f} A {min(n,100):7.3f} B {n/3.2:7.3f} C {max(0,(n-1)/3.19):7.3f} cap {so}->{sn}")
pairs = list(itertools.combinations(tab, 2)); fl = [(a, b) for a, b in pairs if (a[0] - b[0]) * (a[1] - b[1]) < 0]
print(f"\nfile pairs {len(pairs)}; order differs between old raw and corrected raw on {len(fl)}; largest old gap among those {max((abs(a[0]-b[0]) for a,b in fl), default=0):.3f}")
for a, b in sorted(fl, key=lambda p: -abs(p[0][0] - p[1][0]))[:6]:
    print(f"  {a[2]} {a[3]} n={a[5]} vs {b[2]} {b[3]} n={b[5]}: old {a[0]:.3f} vs {b[0]:.3f}; corrected {a[1]:.3f} vs {b[1]:.3f}")
print(f"reports where the number of datasets at the 8x size cap changes: {sum(r['sat_o'] != r['sat_n'] for r in rows)} of {len(rows)}")
ties = {}
for o, n, *_ in tab: ties[min(round(n, 9), 100)] = ties.get(min(round(n, 9), 100), 0) + 1
print(f"files tied at exactly 100 under A: {ties.get(100, 0)} of {len(tab)}")
