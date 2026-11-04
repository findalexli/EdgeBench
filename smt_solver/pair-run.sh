#!/bin/bash
# smt_solver: real solver, full hidden set, old and new judge on ONE worker. Old = the published judge tag; new = that image plus the PR's three changed judge files
# (a sforge build pair leaves too little of the budget for two full grades). 8 CPUs, 7 GiB; official 16 and 16g do not fit the worker. Memory sampled every 30 s.
set -uo pipefail
T=smt_solver; SHA=f92857a3db9d9d5dea274fc81d06e4abcf5bc860; O=/job/out; mkdir -p $O/s $O/inj; cd /job
START=$(date +%s); LIMIT=$(cat /job/limit)
nproc >$O/env.txt; free -m >>$O/env.txt; date -u >>$O/env.txt; docker version --format '{{.Server.Version}}' >>$O/env.txt
curl -LsSf https://astral.sh/uv/install.sh | sh >$O/uv.log 2>&1; export PATH=$HOME/.local/bin:$PATH
git clone -q --filter=blob:none --no-checkout -b community https://github.com/ByteDance-Seed/EdgeBench.git base >$O/clone.log 2>&1
( cd base && git sparse-checkout set --no-cone '/*.md' '/tools/' '/pyproject.toml' '/README*' '/LICENSE' '/sforge/' '/edgebench/benchmark.toml' '/edgebench/bases/' "/edgebench/tasks/$T/" && git checkout -q $SHA ) >>$O/clone.log 2>&1 || { echo clone-failed; exit 2; }
git -C base rev-parse HEAD >>$O/env.txt
uv venv -q --python 3.12 v >>$O/uv.log 2>&1; uv pip install -q --python v/bin/python -e base >>$O/uv.log 2>&1 || { echo install-failed; exit 4; }
tag(){ ( cd $1 && /job/v/bin/python -c "from pathlib import Path; from sforge.harness.task_spec import load_task; print(load_task(Path('edgebench/tasks/$T')).$2)" ); }
OLDKEY=$(tag base judge_image_key | cut -d: -f2); IMGOLD=edgebench.judge.smt_solver:$OLDKEY
docker pull -q docker.io/seededge/edgebench.judge.smt_solver:$OLDKEY >$O/pull.log 2>&1 || { echo pull-failed; exit 5; }
docker tag docker.io/seededge/edgebench.judge.smt_solver:$OLDKEY $IMGOLD
cp -r base new; ( cd new && git apply /job/pr.patch ) >>$O/clone.log 2>&1 || { echo patch-failed; exit 3; }
NT=new/edgebench/tasks/$T/judge
IMGNEW=$(tag new judge_image_key)
mkdir -p ctx; cp $NT/run.sh $NT/parse_result.py $NT/smt_judge/scripts/evaluate.py ctx/
printf 'FROM %s\nCOPY run.sh parse_result.py /judge/\nCOPY evaluate.py /home/workspace/smt_judge/scripts/evaluate.py\n' $IMGOLD > ctx/Dockerfile
docker build -q -t $IMGNEW ctx >$O/newbuild.log 2>&1 || { echo newbuild-failed; exit 6; }
for x in "old $IMGOLD" "new $IMGNEW"; do set -- $x; docker image inspect $2 --format "$1 {{.Id}}" >>$O/tags.txt; docker run --rm --network none --entrypoint sh $2 -c 'find /judge /home/workspace/smt_judge/scripts -type f | sort | xargs sha256sum' >$O/judge-$1.sha 2>&1; done
sed -i 's/^cpus = 16/cpus = 8/; s/^memory = "16g"/memory = "7g"/' base/edgebench/tasks/$T/task.toml new/edgebench/tasks/$T/task.toml
# sforge eval asks for the base image first even when the judge image exists; a local tag satisfies that check, nothing runs on it.
BASEKEY=$(tag base base_image_key); echo "base $BASEKEY" >>$O/tags.txt; docker pull -q docker.io/seededge/edgebench.base.${BASEKEY#*base.} >>$O/pull.log 2>&1 && docker tag docker.io/seededge/edgebench.base.${BASEKEY#*base.} $BASEKEY || docker tag $IMGOLD $BASEKEY
echo "key old $(tag base judge_image_key) new $(tag new judge_image_key)" >>$O/tags.txt
sha256sum /job/subs/* >$O/subs.sha
echo "setup_s $(( $(date +%s)-START ))" >>$O/summary.txt
( while :; do for id in $(docker ps -q --no-trunc); do f=$(find /sys/fs/cgroup -path "*$id*" -name memory.events 2>/dev/null | head -1); d=$(dirname "$f"); echo "$(date +%s) ${id:0:12} cur=$(cat $d/memory.current 2>/dev/null) peak=$(cat $d/memory.peak 2>/dev/null) $(grep -E 'oom_kill|^oom ' $f 2>/dev/null | tr '\n' ' ')"; done; sleep 30; done >>$O/mem.txt ) & SAMP=$!
seval(){ local sd=$2 d; [ $sd = old ] && d=base || d=new
  local el=$(( $(date +%s)-START )); [ $(( el+$4 )) -le $LIMIT ] || { echo "SKIP $1-$sd elapsed=$el" >>$O/summary.txt; return 0; }
  ( cd $d && /job/v/bin/python -m sforge --silent --log-dir /job/sl eval --task $T --archive /job/subs/$3 --run-id $1-$sd --judge-cpu-limit 8 --judge-mem-limit 7g --json ) >$O/s/$1-$sd.log 2>&1
  echo "sforge $1 $sd rc=$? t=$(( $(date +%s)-START ))" >>$O/summary.txt
  cp /job/sl/runs/$1-$sd/$T/submissions/manual-1/judge_output.txt $O/s/$1-$sd.judge_output.txt 2>/dev/null
  cp /job/sl/runs/$1-$sd/$T/submissions/manual-1/report.json $O/s/$1-$sd.report.json 2>/dev/null
}
source /job/arms.sh
kill $SAMP 2>/dev/null; echo done >>$O/summary.txt
