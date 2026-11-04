#!/usr/bin/env python3
"""Inside the judge image, old evaluator. For each input, simulate the validator's recursion depth in file order, with its define cache and without short-circuits: every term is evaluated, as for a model that makes everything true. Frames: eval 1, generator 1 under and/or/+/uf etc, 0 under not/ite/let/compare. Iterative. Prints one JSON line per file with defines."""
import importlib.util, json, multiprocessing as mp
EV = "/home/workspace/smt_judge/scripts/evaluate.py"; H = "/home/workspace/smt_judge/hidden_benchmarks"
sp = importlib.util.spec_from_file_location("ev", EV); ev = importlib.util.module_from_spec(sp); sp.loader.exec_module(ev)
exp = json.load(open(H + "/expected_answers.json"))
GEN = {'and', 'or', '+', '=', 'distinct', '-', '*'}
def one(key):
    forms = ev.parse_smt2(ev.make_solver_input_text(key, f"{H}/{key}", True, "hidden-sebench")); defs = {}; cached = set(); peak = peak_at = 0; n = 0
    for x in forms:
        if not (isinstance(x, list) and x): continue
        if x[0] == 'define-fun' and len(x) == 5:
            if not x[2]: defs[x[1]] = x[4]
        elif x[0] == 'assert' and len(x) == 2:
            n += 1; st = [(x[1], 1)]
            while st:
                t, f = st.pop()
                if f > peak: peak, peak_at = f, n
                if isinstance(t, list):
                    if not t: continue
                    add = 2 if t[0] in GEN or t[0] not in ('not', 'ite', '=>', '<', '>', '<=', '>=', '/', 'let', '!') else 1
                    for c in reversed(t[1:]):
                        if isinstance(c, list) and c and isinstance(c[0], list):
                            for b in c: st.append((b[1], f + add))
                        else: st.append((c, f + add))
                elif t in defs and t not in cached:
                    cached.add(t); st.append((defs[t], f + 1))
    return dict(key=key, expected=exp.get(key), asserts=n, sim_frames=peak, peak_assert=peak_at)
with mp.Pool(4) as p:
    for r in p.imap_unordered(one, sorted(exp)): print(json.dumps(r), flush=True)
