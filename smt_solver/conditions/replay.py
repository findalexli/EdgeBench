#!/usr/bin/env python3
"""Inside the judge image. capture: real solver on all 774 perturbed inputs, 16 at a time, 60 s, keep every sat output. check: old and new validator on identical pairs, each in its own process and on a default main-thread stack as a pool worker has. Prints JSON lines."""
import concurrent.futures as cf, importlib.util, json, os, subprocess, sys, time, hashlib
H = "/home/workspace/smt_judge/hidden_benchmarks"; OLD = "/home/workspace/smt_judge/scripts/evaluate.py"; NEW = "/e/final.py"; CAP = "/cap"
def load(p):
    sp = importlib.util.spec_from_file_location("ev", p); ev = importlib.util.module_from_spec(sp); sp.loader.exec_module(ev); return ev
if sys.argv[1] == 'capture':
    ev = load(OLD); exp = json.load(open(H + "/expected_answers.json")); os.makedirs(CAP, exist_ok=True)
    def one(key):
        name = hashlib.sha256(key.encode()).hexdigest()[:16]; inp = f"/tmp/{name}.smt2"; open(inp, 'w').write(ev.make_solver_input_text(key, f"{H}/{key}", True, "hidden-sebench")); t = time.time()
        p = subprocess.Popen(["./solve", inp], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, start_new_session=True)
        try:
            so, _ = p.communicate(timeout=60); a, w = ev.parse_solver_output(so)
        except subprocess.TimeoutExpired:
            os.killpg(p.pid, 9); p.communicate(); a, w = 'timeout', None
        os.remove(inp)
        if a == 'sat' and w is not None: json.dump(w, open(f"{CAP}/{name}.json", 'w'))
        return dict(key=key, name=name, expected=exp.get(key), answer=a, rc=p.returncode, has_witness=w is not None, secs=round(time.time() - t, 1))
    with cf.ThreadPoolExecutor(16) as ex:
        for r in ex.map(one, sorted(exp)): print(json.dumps(r), flush=True)
elif sys.argv[1] == 'one':
    code, key, wf = sys.argv[2:5]; ev = load(code); inp = f"/tmp/one-{os.getpid()}.smt2"; open(inp, 'w').write(load(OLD).make_solver_input_text(key, f"{H}/{key}", True, "hidden-sebench"))
    try:
        ev.validate_sat_witness(inp, json.load(open(wf))); print("accepted")
    except BaseException as e:
        print("rejected", type(e).__name__, str(e)[:80].replace("\n", " "))
    finally:
        os.remove(inp)
else:
    rows = [json.loads(l) for l in open(sys.argv[2])]; rows = [r for r in rows if r['has_witness']]
    def chk(r):
        out = dict(key=r['key'], expected=r['expected'])
        for side, code in (('old', OLD), ('new', NEW)):
            t = time.time()
            try:
                p = subprocess.run([sys.executable, __file__, 'one', code, r['key'], f"{CAP}/{r['name']}.json"], capture_output=True, text=True, timeout=500); out[side] = p.stdout.strip() or f"rc={p.returncode}"
            except subprocess.TimeoutExpired: out[side] = 'timeout500'
            out[side + '_s'] = round(time.time() - t, 1)
        return out
    with cf.ThreadPoolExecutor(6) as ex:
        for r in ex.map(chk, rows): print(json.dumps(r), flush=True)
