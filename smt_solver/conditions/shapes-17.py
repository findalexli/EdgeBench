#!/usr/bin/env python3
"""Inside the judge image. Deep formulas of many shapes through validate_sat_witness in a pool worker, as the judge calls it. Prints one JSON line per run."""
import concurrent.futures as cf, importlib.util, json, os, resource, sys, time, subprocess
HEAD = "(set-logic QF_UFLRA)\n(declare-fun x () Real)\n(declare-fun p () Bool)\n(declare-fun f (Real) Real)\n"
TAIL = "(check-sat)\n(exit)\n"; C = "(> x 0)"
def body(s, D):
    if s == 'and': return "(assert " + "(and true " * D + C + ")" * D + ")\n"
    if s == 'or': return "(assert " + "(or false " * D + C + ")" * D + ")\n"
    if s == 'not': return "(assert " + "(not " * (2 * (D // 2)) + C + ")" * (2 * (D // 2)) + ")\n"
    if s == 'ite': return "(assert " + "(ite true " * D + C + " false)" * D + ")\n"
    if s == 'imp': return "(assert " + "(=> true " * D + C + ")" * D + ")\n"
    if s == 'xor': return "(assert " + "(xor false " * D + C + ")" * D + ")\n"
    if s == 'eq': return "(assert " + "(= true " * D + C + ")" * D + ")\n"
    if s == 'let': return "(assert " + "(let ((y true)) " * D + C + ")" * D + ")\n"
    if s == 'plus': return "(assert (> " + "(+ 0 " * D + "x" + ")" * D + " 0))\n"
    if s == 'mul': return "(assert (> " + "(* 1 " * D + "x" + ")" * D + " 0))\n"
    if s == 'itea': return "(assert (> " + "(ite true " * D + "x" + " 0)" * D + " 0))\n"
    if s == 'uf': return "(assert (> " + "(f " * D + "x" + ")" * D + " 0))\n"
    if s == 'defplus': return "(define-fun d0 () Real x)\n" + "".join(f"(define-fun d{i} () Real (+ 0 d{i-1}))\n" for i in range(1, D + 1)) + f"(assert (> d{D} 0))\n"
    if s == 'defeq': return "(define-fun d0 () Bool " + C + ")\n" + "".join(f"(define-fun d{i} () Bool (= true d{i-1}))\n" for i in range(1, D + 1)) + f"(assert d{D})\n"
    if s == 'defuf': return "(define-fun d0 () Real x)\n" + "".join(f"(define-fun d{i} () Real (f d{i-1}))\n" for i in range(1, D + 1)) + f"(assert (> d{D} 0))\n"
    if s == 'define': return "(define-fun d0 () Bool " + C + ")\n" + "".join(f"(define-fun d{i} () Bool (and true d{i-1}))\n" for i in range(1, D + 1)) + f"(assert d{D})\n"
    raise SystemExit(s)
def run(code, path):
    sp = importlib.util.spec_from_file_location("ev", code); ev = importlib.util.module_from_spec(sp); sp.loader.exec_module(ev)
    try:
        ev.validate_sat_witness(path, {"values": {"x": "1", "p": "true"}})
    except Exception as e:  # as run_solver_case does; BaseException (ValidatorFailure, SIGSEGV) still reaches the pool
        return "rejected", type(e).__name__, str(e)[:120]
    return "accepted", None, None
if __name__ == '__main__':
    code, s, D = sys.argv[1], sys.argv[2], int(sys.argv[3]); p = f"/tmp/{s}-{D}.smt2"; open(p, 'w').write(HEAD + body(s, D) + TAIL); t = time.time(); r = dict(code=os.path.basename(code), shape=s, depth=D)
    with cf.ProcessPoolExecutor(1) as ex:
        try:
            r['verdict'], r['exc'], r['msg'] = ex.submit(run, code, p).result()
        except BaseException as e:
            r['verdict'] = 'rejected' if isinstance(e, Exception) and not isinstance(e, cf.process.BrokenProcessPool) else 'CRASH'; r['exc'] = type(e).__name__; r['msg'] = str(e)[:120]
    r['secs'] = round(time.time() - t, 1); r['rss_mib'] = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss // 1024; os.remove(p); print(json.dumps(r), flush=True)
