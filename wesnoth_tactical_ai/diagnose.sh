#!/bin/sh
# Install an archive as the judge does, play one game, print the Lua load errors.
# Usage: diagnose.sh <judge-image> <archive.tar.gz>
set -eu
C=wesnoth-lua-diagnose-$$
docker run -d --name "$C" --network none --cpus 4 --memory 8g --entrypoint sleep "$1" infinity >/dev/null
trap 'docker rm -f "$C" >/dev/null' EXIT
docker cp "$2" "$C:/tmp/a.tar.gz"
docker exec -w /home/wesnoth_agent "$C" tar xzf /tmp/a.tar.gz
docker exec -i "$C" python3 - <<'PY'
import os, subprocess, sys
sys.path.insert(0, '/judge')
import eval_wesnoth as e
print('violations', e.scan_for_hacks())
e.install_agent_ai()
cmd = ["/usr/games/wesnoth-1.18", "--nogui", "--multiplayer", "--nosound", "--controller", "1:ai", "--controller", "2:ai",
       "--ai-config", "1:~add-ons/my_ai/my_custom_ai.cfg", "--scenario", "multiplayer_Weldyn_Channel", "--rng-seed", "0", "--turns", "50"]
r = subprocess.run(cmd, capture_output=True, text=True, timeout=180, env={**os.environ, "DISPLAY": ""})
lines = [l for l in (r.stdout + r.stderr).splitlines() if '.lua:' in l and 'add-ons/my_ai' in l]
print('rc', r.returncode, 'lua_error_lines', len(lines))
print('\n'.join(l[:160] for l in lines[:2]))
PY
