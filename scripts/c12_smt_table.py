#!/usr/bin/env python3
"""smt_solver, final judge. Same-host full pairs, reproducer, stack and memory-limit runs, controls, five-file cut. Run from the repo root."""
import collections, glob, json, os, re
for n in (1, 2, 3, 4, 5):
    J = f'evidence/runs/community12-smt-fullpair-{n}/result/'; w = json.load(open(J + 'worker.json')); print(f'--- pair job {n}', w['status'], 'order', open(f'evidence/runs/community12-smt-fullpair-{n}/arms.sh').read().split()[1::4][:2] if 0 else '')
    print(open(f'evidence/runs/community12-smt-fullpair-{n}/arms.sh').read().strip().replace('\n', '; '))
    for s in ('old', 'new'):
        f = J + f'out/s/real-{s}.report.json'
        if not os.path.exists(f): print(s, 'no report'); continue
        r = json.load(open(f)); o = open(J + f'out/s/real-{s}.judge_output.txt').read(); bl = r['metrics'].get('by_logic', {})
        print(s, 'valid', r['valid'], 'score', round(r['score_0_100'], 2), r['summary'].split(', ')[-1], 'grade_s', round(r['runtime_seconds']), 'BrokenProcessPool', o.count('BrokenProcessPool'), {k: (v['correct'], v['invalid_model'], v['timeout'], v['error']) for k, v in bl.items()})
    last = {}
    for l in open(J + 'out/mem.txt'):
        p = l.split()
        if 'oom_kill' not in p: continue
        e = last.setdefault(p[1], dict(t0=int(p[0]), oom=0, firstoom=None)); o = int(p[p.index('oom_kill') + 1]); e['t1'] = int(p[0])
        if o and e['firstoom'] is None: e['firstoom'] = int(p[0]) - e['t0']
        e['oom'] = max(e['oom'], o)
    for k, e in last.items(): print(' container', k, 'sampled_s', e['t1'] - e['t0'], 'oom_kill', e['oom'], 'first_at_s', e['firstoom'])
    print(' judge files, new, same as sforge build image:', sorted(l for l in open(J + 'out/judge-new.sha') if re.search('evaluate|parse_result|run.sh', l)) == sorted(l for l in open('evidence/runs/community12-smt-checks/result/out/judge-new.sha') if re.search('evaluate|parse_result|run.sh', l)))
M = 'evidence/runs/community12-smt-checks/result/'; print('--- checks job', json.load(open(M + 'worker.json'))['status'], open(M + 'out/tags.txt').readline().strip()); M += 'out/'
g = collections.defaultdict(list)
for f in glob.glob(M + 's/*.report.json'):
    a, p, s = os.path.basename(f)[:-len('.report.json')].rsplit('-', 2); r = json.load(open(f)); g[(a, s)].append((round(r['score_0_100'], 2), r['valid'], r['summary'].split(', ')[-1], round(r['runtime_seconds'])))
for k in sorted(g): print(k, g[k])
for f in sorted(glob.glob(M + 'five/*.json') + glob.glob(M + 'g/*.json')):
    r = json.load(open(f)); print(os.path.basename(f), r.get('score_0_100'), r.get('valid'), r.get('summary'), round(r.get('runtime_s') or 0))
print('--- direct run.sh under a shell limit, reproducer')
for f in sorted(glob.glob(M + 'inj/*.log')) + sorted(glob.glob('evidence/runs/community12-smt-fullpair-2.attempt2-result/out/inj/*.log')) + sorted(glob.glob('evidence/runs/community12-smt-fullpair-2.sparse-attempt-result/out/inj/*.log')):
    t = open(f).read(); j = json.loads(t.strip().splitlines()[-1]); m = re.search(r'ValidatorFailure: .*|BrokenProcessPool', t)
    print(os.path.basename(f)[:-4], 'stack,as', t.split('\n')[0], t.split('\n')[1], '|', j['valid'], j['summary'], '|', m.group(0)[:60] if m else '')
