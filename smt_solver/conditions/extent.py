#!/usr/bin/env python3
"""Inside the judge image, old evaluator. How many of the 774 inputs nest as deeply as the five known files? Static: maximum parenthesis depth of the perturbed input, iterative. Prints one JSON line per file."""
import importlib.util, json, sys, multiprocessing as mp
EV = "/home/workspace/smt_judge/scripts/evaluate.py"; H = "/home/workspace/smt_judge/hidden_benchmarks"
sp = importlib.util.spec_from_file_location("ev", EV); ev = importlib.util.module_from_spec(sp); sp.loader.exec_module(ev)
exp = json.load(open(H + "/expected_answers.json"))
def one(key):
    t = ev.make_solver_input_text(key, f"{H}/{key}", True, "hidden-sebench"); d = m = 0; q = False; c = False
    for ch in t:
        if c:
            c = ch != '\n'
        elif q:
            q = ch != '|'
        elif ch == ';': c = True
        elif ch == '|': q = True
        elif ch == '(':
            d += 1; m = max(m, d)
        elif ch == ')': d -= 1
    return dict(key=key, expected=exp.get(key), size=len(t), paren_depth=m, lets=t.count('(let '), ites=t.count('(ite '))
with mp.Pool(6) as p:
    for r in p.imap_unordered(one, sorted(exp)): print(json.dumps(r), flush=True)
