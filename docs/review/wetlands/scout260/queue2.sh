#!/bin/bash
# Load-aware rest of the screen: at most 2 of my jobs at once; a job starts only when the 1-min load <= 30.
S=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/s260
W=/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-ac502a6f660c0286b
cd "${S:?}" || exit 1
export PLANET_DATA="${S:?}/data" NUMBA_NUM_THREADS=4 OMP_NUM_THREADS=4
mine() { ps -eo args | grep "s260/fork_run.py cont" | grep -v grep | grep -vc "uv run"; }
for j in "1 cand 0" "1 cand 1" "77 main 0" "77 cand 0" "77 main 1" "77 cand 1"; do
  set -- $j
  while true; do
    load=$(cut -d' ' -f1 /proc/loadavg)
    if [ "$(mine)" -lt 2 ] && python3 -c "import sys; sys.exit(0 if $load <= 30 else 1)"; then break; fi
    sleep 20
  done
  off=$(python3 -c "print($3*1e-5)")
  uv run --project "$W" python "${S:?}/fork_run.py" cont "${S:?}/code/$2" "${S:?}/s$1.ckpt" --seed "$1" --level 6 \
    --myr 400 --offset "$off" --name "s$1_$2_d$3" > "${S:?}/cont_s$1_$2_d$3.log" 2>&1 &
  sleep 15
done
wait
while [ "$(mine)" -gt 0 ]; do sleep 20; done
echo ALLDONE
