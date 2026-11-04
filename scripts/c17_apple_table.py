#!/usr/bin/env python3
"""Apple, final patch (timeout_sec 1800). Second pairs on six files (community17-apple-more-c) joined to community13 pairs; limits 2 and 1 (community17-apple-lim2, -lim1).
Usage: c17_apple_table.py [runs_dir]. Pair order: first side graded on the worker is listed."""
import glob, json, os, re, sys

RUNS = sys.argv[1] if len(sys.argv) > 1 else "evidence/runs"
rows, secs, starts = {}, {}, {}
for job in ("community13-apple-more-a", "community13-apple-more-b", "community17-apple-more-c"):
    out = f"{RUNS}/{job}/result/out"
    assert json.load(open(f"{RUNS}/{job}/result/worker.json"))["status"] == "exit=0", job
    tag = re.search(r"judge\.apple_incremental_game:(\w+) new \S+:(\w+)", open(f"{out}/tags.txt").read())
    print(job, "old key", tag[1], "new key", tag[2])
    for line in open(f"{out}/summary.txt"):
        m = re.match(r"arm hot4-s(\w+)-(old|new)-r(\d) side=\w+ sub=\w+ rc=0 start=(\d+) end=(\d+) online=0-3", line)
        if m:
            secs[(m[1], m[2], m[3])] = int(m[5]) - int(m[4]); starts[(m[1], m[2], m[3])] = int(m[4])
    for f in glob.glob(f"{out}/s/hot4-*.report.json"):
        m = re.match(r"hot4-s(\w+)-(old|new)-r(\d)\.report", os.path.basename(f))
        r = json.load(open(f))
        passed = sum(d["status"] == "PASSED" for d in r["details"])
        rows.setdefault(m[1], {}).setdefault(m[3], {})[m[2]] = (r["score_0_100"], r["score"], passed, r["valid"], r["runtime_seconds"])
deltas, minima, imp = [], [], {}
print("submission round first old new delta raw_delta_% old_ok new_ok old_runtime_s new_runtime_s old_cmd_s new_cmd_s")
for sub in sorted(rows):
    for rd in sorted(rows[sub]):
        old, new = rows[sub][rd]["old"], rows[sub][rd]["new"]
        assert old[3] and new[3]
        d = new[0] - old[0]; deltas.append(d); minima.append(min(old[2], new[2])); imp.setdefault(sub, []).append(d)
        first = "old" if starts[(sub, "old", rd)] < starts[(sub, "new", rd)] else "new"
        print(sub, rd, first, f"{old[0]:.2f} {new[0]:.2f} {d:+.2f} {100 * (new[1] / old[1] - 1):+.2f} {old[2]} {new[2]} {old[4]:.1f} {new[4]:.1f} {secs[(sub, 'old', rd)]} {secs[(sub, 'new', rd)]}")
print(f"submissions={len(rows)} pairs={len(deltas)} delta_min={min(deltas):+.2f} delta_max={max(deltas):+.2f} lower_on_new={sum(d < -0.005 for d in deltas)} cases_min={min(minima)}")
up = {k: v for k, v in imp.items() if max(v) > 0.5}
print(f"moved files={len(up)} pairs={sum(map(len, up.values()))} range {min(map(min, up.values())):+.2f} {max(map(max, up.values())):+.2f}; unmoved files={len(imp) - len(up)} pairs={sum(len(v) for k, v in imp.items() if k not in up)} range {min(min(v) for k, v in imp.items() if k not in up):+.2f} {max(max(v) for k, v in imp.items() if k not in up):+.2f}")
print("max_new_cmd_s", max(v for k, v in secs.items() if k[1] == "new"), "max_old_cmd_s", max(v for k, v in secs.items() if k[1] == "old"))
print("--- lower --judge-cpu-limit, one file, timeout_sec 1800 on new, order as graded")
for job in ("community17-apple-lim2", "community17-apple-lim1"):
    out = f"{RUNS}/{job}/result/out"
    assert json.load(open(f"{RUNS}/{job}/result/worker.json"))["status"] == "exit=0", job
    for line in open(f"{out}/summary.txt"):
        m = re.match(r"arm (\S+) side=(\w+) lim=(\d) rc=(\d+) start=(\d+) end=(\d+)", line)
        if not m:
            continue
        f = f"{out}/s/{m[1]}.report.json"
        if os.path.exists(f):
            r = json.load(open(f)); passed = sum(d["status"] == "PASSED" for d in r["details"])
            print(m[1], "limit", m[3], "rc", m[4], "cmd_s", int(m[6]) - int(m[5]), "valid", r["valid"], "score", round(r["score_0_100"], 2), f"{passed}/{len(r['details'])}", "runtime_s", round(r["runtime_seconds"], 1))
        else:
            print(m[1], "limit", m[3], "rc", m[4], "cmd_s", int(m[6]) - int(m[5]), "no report")
