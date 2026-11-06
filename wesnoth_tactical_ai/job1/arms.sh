# One raw game per side per Lua archive, installed exactly as the judge does: does the file load?
cat > /job/g.py <<'PY'
import sys, os, subprocess
sys.path.insert(0, '/judge'); import eval_wesnoth as e
print('violations', e.scan_for_hacks()); e.install_agent_ai()
cmd = ["/usr/games/wesnoth-1.18","--nogui","--multiplayer","--nosound","--controller","1:ai","--controller","2:ai","--ai-config","1:~add-ons/my_ai/my_custom_ai.cfg","--scenario","multiplayer_Weldyn_Channel","--rng-seed","0","--turns","50"]
r = subprocess.run(cmd, capture_output=True, text=True, timeout=180, env={**os.environ,"DISPLAY":""})
out = r.stdout + r.stderr; open('/tmp/game.log','w').write(out)
ls = [l for l in out.splitlines() if '.lua:' in l and 'add-ons/my_ai' in l]
print('rc', r.returncode, 'lua_error_lines', len(ls), 'RECRUIT_lines', sum(l.startswith('RECRUIT') for l in out.splitlines()))
print('\n'.join(l[:220] for l in ls[:3]))
PY
one(){ local sd=$1 img=$2 ar=$3 C=w1-$1-$3; docker run -d --name $C --network none --cpus 4 --memory 8g --entrypoint sleep $img infinity >/dev/null
  docker cp /job/subs/$ar.tar.gz $C:/tmp/a.tar.gz; docker exec -w /home/wesnoth_agent $C sh -c 'tar xzf /tmp/a.tar.gz'
  docker cp /job/g.py $C:/tmp/g.py; docker exec $C python3 /tmp/g.py >$O/d/one-$sd-$ar.txt 2>&1; docker cp $C:/tmp/game.log $O/d/one-$sd-$ar.log; docker rm -f $C >/dev/null; }
for ar in lua hold example; do one old $IMGOLD $ar; one new $IMGNEW $ar; done
echo "one_games_done t=$(( $(date +%s)-START ))" >>$O/summary.txt
# Official grades, old first then new, interleaved.
for r in 1 2; do for ar in hold rca lua; do seval $ar-$r old $ar.tar.gz 200; seval $ar-$r new $ar.tar.gz 200; done; done
seval starter-1 old starter.tar.gz 100; seval starter-1 new starter.tar.gz 100
seval example-1 old example.tar.gz 200; seval example-1 new example.tar.gz 200
