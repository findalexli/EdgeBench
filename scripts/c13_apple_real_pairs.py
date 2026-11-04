#!/usr/bin/env python3
"""Apple: real agent submissions, old vs new judge, true 4 vCPUs online, one judge at a time (community13-apple-more-a, -b).
Also the SFORGE_CPUS values tried on the new judge. Usage: c13_apple_real_pairs.py [runs_dir]"""
import glob, json, os, re, sys

RUNS = sys.argv[1] if len(sys.argv) > 1 else "evidence/runs"
rows, secs = {}, {}
for job in ("community13-apple-more-a", "community13-apple-more-b"):
    out = f"{RUNS}/{job}/result/out"
    assert json.load(open(f"{RUNS}/{job}/result/worker.json"))["status"] == "exit=0", job
    for line in open(f"{out}/summary.txt"):
        m = re.match(r"arm hot4-s(\w+)-(old|new)-r(\d) side=\w+ sub=\w+ rc=0 start=(\d+) end=(\d+) online=0-3", line)
        if m:
            secs[(m[1], m[2], m[3])] = int(m[5]) - int(m[4])
    for f in glob.glob(f"{out}/s/hot4-*.report.json"):
        m = re.match(r"hot4-s(\w+)-(old|new)-r(\d)\.report", os.path.basename(f))
        r = json.load(open(f))
        passed = sum(d["status"] == "PASSED" for d in r["details"])
        rows.setdefault(m[1], {}).setdefault(m[3], {})[m[2]] = (r["score_0_100"], r["score"], passed, r["valid"])
pairs = 0; deltas = []; minima = []
print("submission round old_score new_score delta raw_delta_% old_ok new_ok old_s new_s")
for sub in sorted(rows):
    for rd in sorted(rows[sub]):
        old, new = rows[sub][rd]["old"], rows[sub][rd]["new"]
        d = new[0] - old[0]; pairs += 1; deltas.append(d); minima.append(min(old[2], new[2]))
        assert old[3] and new[3]
        print(sub, rd, f"{old[0]:.2f} {new[0]:.2f} {d:+.2f} {100 * (new[1] / old[1] - 1):+.2f} {old[2]} {new[2]} {secs[(sub, 'old', rd)]} {secs[(sub, 'new', rd)]}")
print(f"submissions={len(rows)} pairs={pairs} delta_min={min(deltas):+.2f} delta_max={max(deltas):+.2f} lower_on_new={sum(d < 0 for d in deltas)} cases_min={min(minima)}")
print("max_new_s", max(v for k, v in secs.items() if k[1] == "new"), "max_old_s", max(v for k, v in secs.items() if k[1] == "old"))
print("SFORGE_CPUS on the new judge, valid answer plus 1 s per case, 8 vCPUs online:")
for line in open(f"{RUNS}/community13-apple-more-b/result/out/summary.txt"):
    m = re.match(r"env \[(.*?)\] rc=\d+ wall=([\d.]+) .*?\"valid\": (\w+), \"summary\": \"([^\"]*)\"", line)
    if m:
        print(f"  [{m[1]}] wall={m[2]} valid={m[3]} {m[4][:40]}")
