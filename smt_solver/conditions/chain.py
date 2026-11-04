#!/usr/bin/env python3
"""Inside the judge image, old evaluator. Static bound on validator recursion for each of the 774 perturbed inputs, whatever the model: longest path through nested terms and define-fun references. Bound on Python frames: 2 per term level (eval plus generator), 1 per symbol or reference. Definitions precede use in SMT-LIB, so one forward pass is enough. Prints one JSON line per file."""
import collections, importlib.util, json, multiprocessing as mp
EV = "/home/workspace/smt_judge/scripts/evaluate.py"; H = "/home/workspace/smt_judge/hidden_benchmarks"
sp = importlib.util.spec_from_file_location("ev", EV); ev = importlib.util.module_from_spec(sp); sp.loader.exec_module(ev)
exp = json.load(open(H + "/expected_answers.json"))
def walk(term, D, F, ops):
    bd = bf = 0; st = [(term, 0, 0)]
    while st:
        t, d, f = st.pop()
        if isinstance(t, list):
            if t and isinstance(t[0], str): ops[t[0]] += 1
            st.extend((c, d, f + 2) for c in t)
        else:
            bd = max(bd, d + D.get(t, 0) + (1 if t in D else 0)); bf = max(bf, f + 1 + F.get(t, 0))
    return bd, bf
def one(key):
    forms = ev.parse_smt2(ev.make_solver_input_text(key, f"{H}/{key}", True, "hidden-sebench")); D = {}; F = {}; ops = collections.Counter(); ad = af = na = 0
    for x in forms:
        if isinstance(x, list) and x and x[0] == 'define-fun' and len(x) == 5:
            D[x[1]], F[x[1]] = walk(x[4], D, F, ops)
        elif isinstance(x, list) and x and x[0] == 'assert' and len(x) == 2:
            a, b = walk(x[1], D, F, ops); ad = max(ad, a); af = max(af, b); na += 1
    return dict(key=key, expected=exp.get(key), defines=len(D), asserts=na, chain=ad, frames_bound=af, ops=ops.most_common(8))
with mp.Pool(6) as p:
    for r in p.imap_unordered(one, sorted(exp)): print(json.dumps(r), flush=True)
