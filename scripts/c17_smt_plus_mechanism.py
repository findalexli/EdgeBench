#!/usr/bin/env python3
"""Deep (+ 0 ...) at a lowered limit: shows `unknown symbol 0` comes from the recursion limit reached inside literal parsing. Usage: c17_smt_plus_mechanism.py <evaluate.py>"""
import importlib.util, sys, tempfile, threading
sp = importlib.util.spec_from_file_location("ev", sys.argv[1]); ev = importlib.util.module_from_spec(sp); sp.loader.exec_module(ev)
HEAD = "(set-logic QF_UFLRA)\n(declare-fun x () Real)\n(declare-fun p () Bool)\n(declare-fun f (Real) Real)\n"
ev.VALIDATOR_RECURSION_LIMIT = 3000; ev.VALIDATOR_STACK_BYTES = 256 * 1024**2
for D in (100, 200, 400, 800, 1500, 3000, 6000):
    p = tempfile.mktemp(suffix=".smt2"); open(p, "w").write(HEAD + "(assert (> " + "(+ 0 " * D + "x" + ")" * D + " 0))\n(check-sat)\n(exit)\n")
    try:
        ev.validate_sat_witness(p, {"values": {"x": "1", "p": "true"}}); print(D, "accepted")
    except Exception as e:
        print(D, type(e).__name__, str(e)[:60])
