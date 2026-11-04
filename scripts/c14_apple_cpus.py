#!/usr/bin/env python3
"""Apple: one real file (the 28 s one) under lower judge CPU limits than the official 4 (community14-apple-cpus). Usage: c14_apple_cpus.py [runs_dir]"""
import json, re, sys
RUNS = sys.argv[1] if len(sys.argv) > 1 else "evidence/runs"
out = f"{RUNS}/community14-apple-cpus/result"
assert json.load(open(f"{out}/worker.json"))["status"] == "exit=0"
for line in open(f"{out}/out/summary.txt"):
    m = re.match(r"arm (\S+) side=(\w+) lim=(\d+) rc=\d+ start=(\d+) end=(\d+)", line)
    if m:
        r = json.load(open(f"{out}/out/s/{m[1]}.report.json"))
        print(f"limit={m[3]} {m[2]} wall={int(m[5]) - int(m[4])}s valid={r['valid']} timed_out={r['timed_out']} score={r['score_0_100']} {str(r.get('summary'))[:45]} {r.get('error') or ''}")
