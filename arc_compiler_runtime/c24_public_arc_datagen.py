#!/usr/bin/env python3
"""Count public submissions that lose Arc's type-system suites or Datagen's Phase 1.
usage: c24_public_arc_datagen.py <dir> [<dir> ...]   (dirs of fetched public reports; read-only)"""
import json, os, re, sys
TS = re.compile(r'^\s*(\S*type-system\S*)\s+(\d+)\s*/\s*(\d+)', re.M)
P1 = re.compile(r'Phase 1: (\d+)/(\d+) checks passed')
def entries(path):
    d = json.load(open(path))
    if isinstance(d, dict) and 'task_id' in d and ('details' in d or 'summary' in d):
        yield d; return
    seq = d.get('entries', d.get('history', [])) if isinstance(d, dict) else d
    if isinstance(d, dict) and 'report' in d: seq = [d['report']]
    for e in seq if isinstance(seq, list) else []:
        r = e.get('report', e) if isinstance(e, dict) else None
        if isinstance(r, dict): yield r
def text(r): return json.dumps(r)
rows = {}
for root in sys.argv[1:]:
    for dp, _, fs in os.walk(root):
        for f in fs:
            if not f.endswith('.json'): continue
            p = os.path.join(dp, f)
            task = 'arc' if 'arc_compiler_runtime' in p else 'datagen' if 'schemathesis_datagen' in p else None
            if not task: continue
            src = root.rstrip('/').split('/')[-1]
            try: es = list(entries(p))
            except Exception: continue
            for r in es:
                s = text(r).replace('\\n', '\n')
                sc = r.get('score')
                if task == 'arc':
                    m = TS.findall(s)
                    if not m: continue
                    got = sum(int(a) for _, a, b in m); tot = sum(int(b) for _, a, b in m)
                    key = (src, task); rows.setdefault(key, []).append((got, tot, sc, p))
                else:
                    m = P1.search(s)
                    if not m: continue
                    rows.setdefault((src, task), []).append((int(m[1]), int(m[2]), sc, p))
for (src, task), v in sorted(rows.items()):
    seen = {}
    for got, tot, sc, p in v: seen[(p, got, tot, sc)] = 1
    v = [k for k in seen]
    zero = [x for x in v if x[1] == 0]
    tots = sorted({x[2] for x in v})
    best = max((x[3] or 0) for x in v)
    bestz = max(((x[3] or 0) for x in zero), default=None)
    print(f'{src} {task}: graded {len(v)}, zero on suite {len(zero)}, suite totals {tots}, best score {best}, best score among zero {bestz}')
