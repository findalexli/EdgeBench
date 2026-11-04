#!/usr/bin/env python3
"""apple_incremental_game, every sforge eval report of community9-* and community10-apple-r1, by file and condition, nothing left out.
Pairs are as labelled in the job (same pass, same worker). Also the 89 reports of the original agent runs. Run from the repo root."""
import collections, glob, hashlib, json, os, re, tarfile
rows = collections.defaultdict(list); pairs = collections.defaultdict(dict)
for job in sorted(glob.glob('evidence/runs/community9-apple_incremental_game-*/')) + ['evidence/runs/community10-apple-r1/']:
    assert json.load(open(job + 'result/worker.json'))['status'] == 'exit=0', job
    name = os.path.basename(job[:-1]).replace('community9-apple_incremental_game-', 'c9').replace('community10-apple-', 'c10')
    for f in glob.glob(job + 'result/out/s/*.report.json'):
        m = re.fullmatch(r'([a-z0-9]+)-([a-z0-9]+)-(old|new)-(r\d+(?:-k\d+)?)', os.path.basename(f)[:-len('.report.json')])
        if not m: continue
        d = json.load(open(f)); cond, sub, side, rep = m.groups()
        rows[(sub, cond, side)].append((d['score_0_100'], d['metrics']['cases_passed'], d['runtime_seconds'], name, d['valid']))
        assert side not in pairs[(sub, cond, name, rep)], f
        pairs[(sub, cond, name, rep)][side] = d['score_0_100']
print('sub cond judge n workers score_range ok_range max_runtime_s all_valid')
for k in sorted(rows):
    v = rows[k]; s = [x[0] for x in v]; o = [x[1] for x in v]
    print(*k, len(v), ','.join(sorted({x[3] for x in v})), f'{min(s):.2f}-{max(s):.2f}', f'{min(o)}-{max(o)}', f'{max(x[2] for x in v):.1f}', all(x[4] for x in v))
print('--- matched pairs, new minus old')
g = collections.defaultdict(list)
for (sub, cond, name, rep), v in sorted(pairs.items()):
    if len(v) == 2: g[(sub, cond)].append(v['new'] - v['old'])
for k in sorted(g): print(*k, 'n', len(g[k]), f'{min(g[k]):.2f}..{max(g[k]):.2f}', 'mean', f'{sum(g[k])/len(g[k]):.2f}')
h = g[('fork', 'hot4')] + g[('st', 'hot4')]; print('deadline files, true 4 CPUs: pairs', len(h), f'{min(h):.2f}..{max(h):.2f}')
print('--- file hashes')
for n, p in (('fast', 'a/subs/fast'), ('fix80', 'a/subs/fix80'), ('fork', 'a/subs/fork'), ('st', 'b/subs/st')):
    t = tarfile.open(f'evidence/runs/community9-apple_incremental_game-{p}.tar.gz'); s = t.extractfile([m for m in t if m.name.endswith('solution.py')][0]).read()
    print(n, hashlib.sha256(s).hexdigest(), len(s), 'bytes')
print('--- original agent runs')
c = collections.Counter(); same = collections.defaultdict(list)
for rj in glob.glob('evidence/runs/claude-opus-apple_incremental_game*/result/out/sforge-logs/runs/*/apple_incremental_game/submissions/*/report.json'):
    r = json.load(open(rj)); c[r['summary'].split()[0]] += 1
    same[hashlib.sha256(open(rj.replace('report.json', 'submission.tar.gz'), 'rb').read()).hexdigest()[:10]].append(r['score_0_100'])
print('reports', sum(c.values()), dict(c)); 
for k, v in same.items():
    if len(v) > 1: print('same archive', k, 'n', len(v), f'{min(v):.2f}-{max(v):.2f}')
print('--- the 28 s file under 5 judges at once, by worker')
for side in ('old', 'new'):
    w = collections.defaultdict(list)
    for x in rows[('fork', 'x5', side)]: w[x[3]].append(x)
    for k in sorted(w): print(side, k, 'n', len(w[k]), f'{min(x[0] for x in w[k]):.2f}-{max(x[0] for x in w[k]):.2f}', f'ok {min(x[1] for x in w[k])}-{max(x[1] for x in w[k])}')
