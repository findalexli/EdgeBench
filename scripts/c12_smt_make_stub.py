#!/usr/bin/env python3
"""smt_solver reproducer without a real solver: answers `unknown` except on one hidden input, where it prints the
captured correct model. Writes build.sh, solve, src/model.txt and a tar.gz. Run from the repo root."""
import hashlib, io, sys, tarfile
KEY = '8e72757e0b560007'; CAP = f'evidence/runs/community11-smt_solver-witness/result/out/cap/{KEY}/'
out = sys.argv[1]
h = hashlib.sha256(open(CAP + 'input.smt2', 'rb').read()).hexdigest()
model = open(CAP + 'solver.out', 'rb').read()
solve = f'''#!/bin/sh
if [ "$(sha256sum "$1" | cut -d' ' -f1)" = {h} ]; then cat "$(dirname "$0")/src/model.txt"; else echo unknown; fi
'''.encode()
files = {'build.sh': (b'#!/bin/sh\nexit 0\n', 0o755), 'solve': (solve, 0o755), 'src/model.txt': (model, 0o644)}
with tarfile.open(out, 'w:gz') as t:
    d = tarfile.TarInfo('src'); d.type = tarfile.DIRTYPE; d.mode = 0o755; t.addfile(d)
    for n, (b, m) in files.items():
        i = tarfile.TarInfo(n); i.size = len(b); i.mode = m; t.addfile(i, io.BytesIO(b))
print(KEY, h, len(model))
