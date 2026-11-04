#!/usr/bin/env python3
"""apple_incremental_game: old pool (8 at once) vs new pool (min(8, SFORGE_CPUS, cases)). Run from the repo root.
Reads every sforge eval report of community9-apple_incremental_game-{a..e,smoke} and community10-apple-r1, and the earlier judge_local grades of community-apple_incremental_game-r1..r6. Conditions: hot4 = 4 vCPUs online, one judge at a time; q4 = 8 online, one judge at a time, quota 4; x5 = 8 online, 5 judges at once, each quota 4, about 1.6 CPUs each."""
import glob, json, os, re
rows = {}; jobs = sorted(glob.glob('evidence/runs/community9-apple_incremental_game-*/')) + ['evidence/runs/community10-apple-r1/']
for job in jobs:
    w = json.load(open(job + 'result/worker.json')); print(os.path.basename(job[:-1]), w.get('status'), open(job + 'result/out/tags.txt').readline().strip() if os.path.exists(job + 'result/out/tags.txt') else '')
    for f in glob.glob(job + 'result/out/s/*.report.json'):
        lab = os.path.basename(f)[:-len('.report.json')]; m = re.match(r'([a-z0-9]+)-([a-z0-9]+)-(old|new)-(r\d+)', lab)
        if not m: continue
        d = json.load(open(f)); mt = d.get('metrics') or {}
        rows.setdefault((m.group(2), m.group(1), m.group(3), 'c10' if 'community10' in job else 'c9'), []).append((d.get('score_0_100'), mt.get('cases_passed'), d.get('runtime_seconds'), d.get('valid')))
print('sub cond judge src n score_range cases_ok_range max_runtime_s all_valid')
for k in sorted(rows):
    v = rows[k]; s = [x[0] for x in v]; o = [x[1] for x in v]
    print(*k, len(v), f'{min(s):.2f}-{max(s):.2f}', f'{min(o)}-{max(o)}', f'{max(x[2] for x in v):.0f}', all(x[3] for x in v))
print('--- worst case under timeout_sec 600: every case at the 30 s limit, judge_local, 3 workers')
g = {}
for f in glob.glob('evidence/runs/community-apple_incremental_game-r[123]/result/out/g/*.json'):
    m = re.match(r'(.+)-(old|new)\.json', os.path.basename(f))
    if not m: continue
    d = json.load(open(f)); g.setdefault((m.group(1), m.group(2)), []).append((d.get('score_0_100'), d.get('runtime_s'), d.get('summary')))
for k in sorted(g):
    v = g[k]; print(*k, 'n', len(v), 'scores', sorted({round(x[0] or 0, 2) for x in v}), 'runtime', f'{min(x[1] for x in v):.0f}-{max(x[1] for x in v):.0f}', v[0][2][:40])
print('--- same fork file, judge_local, one judge at a time, quota 4 on 8 vCPU, old pool, by worker (host load not controlled)')
for j in ('r4', 'r5', 'r6'):
    v = [json.load(open(f)) for f in sorted(glob.glob(f'evidence/runs/community-apple_incremental_game-{j}/result/out/g/real2-p*-old.json'))]
    n = [json.load(open(f)) for f in sorted(glob.glob(f'evidence/runs/community-apple_incremental_game-{j}/result/out/g/real2-p*-new.json'))]
    print(j, 'old', [(x['summary'].split()[0], round(x['score_0_100'], 2)) for x in v], 'new', [(x['summary'].split()[0], round(x['score_0_100'], 2)) for x in n])
print('--- worker e single-process speed during its run (calib.txt)')
print(open('evidence/runs/community9-apple_incremental_game-e/result/out/calib.txt').read().strip())
print('--- clock use in the real files (solution.py)')
import hashlib, tarfile
for n, p in (('fast', 'a/subs/fast'), ('fix80', 'a/subs/fix80'), ('fork', 'a/subs/fork'), ('st', 'b/subs/st')):
    t = tarfile.open(f'evidence/runs/community9-apple_incremental_game-{p}.tar.gz'); s = t.extractfile([m for m in t if m.name.endswith('solution.py')][0]).read().decode()
    print(n, 'reads time.time()', 'time.time' in s, re.findall(r'time\.time\(\) - \w+ > [\w.]+', s)[:2], re.findall(r'^TL\s*=.*', s, re.M)[:1])
print('--- fixed CPU per case, official path: sforge eval, SFORGE_CPUS=4, judge limited to 4 CPUs of 8 vCPUs, one judge at a time (community11-apple_incremental_game-a)')
J = 'evidence/runs/community11-apple_incremental_game-a/result/'
print(json.load(open(J + 'worker.json'))['status'], open(J + 'out/tags.txt').readline().strip())
for line in open(J + 'out/summary.txt'):
    m = re.match(r'sforge (\S+) (old|new) rc=(\d+) wall=(\d+)', line)
    if not m: continue
    r = json.load(open(glob.glob(f'{J}out/sf/runs/{m.group(1)}-{m.group(2)}/**/report.json', recursive=True)[0]))
    print(m.group(1), m.group(2), 'rc', m.group(3), 'score', round(r['score_0_100'], 2), r['summary'].split('.')[0], 'valid', r['valid'], 'grade_s', round(r['runtime_seconds']))
print('--- raw totals of the 20 s control, official path')
for f in sorted(glob.glob('evidence/runs/community11-apple_incremental_game-a/result/out/sf/runs/cpu20-*/**/report.json', recursive=True)):
    d = json.load(open(f)); print(f.split('/runs/')[-1].split('/')[0], 'total', d['score'], 'normalized', round(d['score_0_100'], 4))
