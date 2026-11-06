#!/usr/bin/env python3
"""Wesnoth Lua header pair: official grades and raw-game load errors, old and new judge.
Usage: c20_wesnoth_lua.py <job>/result/out [<job2>/result/out]"""
import glob, json, os, re, sys

outs = sys.argv[1:]
out = outs[0]
grades = {}
for f in sorted(f for o in outs for f in glob.glob(f"{o}/s/*.log")):
    label = os.path.basename(f)[:-4]
    arm, rep, side = label.rsplit("-", 2)
    d = json.loads(re.search(r"^\{.*\}", open(f).read(), re.S | re.M).group(0))
    assert d["valid"] is True and d["timed_out"] is False, label
    m = d["metrics"]
    grades.setdefault(arm, {}).setdefault(side, []).append((int(rep), d["score_0_100"], m["cases_passed"], round(d["runtime_seconds"])))
for arm, sides in grades.items():
    for side in ("old", "new"):
        rows = sorted(sides[side])
        print(arm, side, "scores", [r[1] for r in rows], "wins", [r[2] for r in rows], "runtime_s", [r[3] for r in rows])
for f in sorted(glob.glob(f"{out}/d/one-*.txt")):
    t = open(f).read()
    print(os.path.basename(f)[:-4], re.search(r"violations .*", t).group(0), re.search(r"lua_error_lines \d+", t).group(0))
hits = []
for o in outs:
    found = [h for arm in ("hold", "lua", "example") for h in
             glob.glob(f"{o}/sf/runs/{arm}-*-old/**/judge_output.txt", recursive=True) + glob.glob(f"{o}/judge_output/{arm}-*-old.txt")]
    assert found, f"no judge output under {o}"
    hits += found
print("old judge_output files for Lua archives", len(hits), "mentioning the load error", sum("must be assigned" in open(h, errors="replace").read() for h in hits))
