"""Fault injection: MemoryError while parsing a numeric literal must end the evaluation, not reject the model. Usage: c17_smt_memory_fault.py <evaluate.py>"""
import importlib.util, sys
sp = importlib.util.spec_from_file_location("ev", sys.argv[1]); ev = importlib.util.module_from_spec(sp); sys.modules["ev"] = ev; sp.loader.exec_module(ev)
open("/tmp/claude-1000/-home-alex-edgebench-verified/inj.smt2", "w").write("(set-logic QF_LRA)\n(declare-fun x () Real)\n(assert (> 3 1))\n(check-sat)\n")
ev.validate_sat_witness("/tmp/claude-1000/-home-alex-edgebench-verified/inj.smt2", {"values": {"x": "2"}}); print("control accepted")
real = ev.parse_numeric_literal
def boom(t): raise MemoryError("injected")
ev.parse_numeric_literal = boom
try:
    ev.validate_sat_witness("/tmp/claude-1000/-home-alex-edgebench-verified/inj.smt2", {"values": {"x": "2"}}); print("accepted")
except BaseException as e:
    print(type(e).__name__, e)
