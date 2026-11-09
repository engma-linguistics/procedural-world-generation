#!/bin/bash
# PW-831 scout 260 screen: spin seeds to 200 Myr on main, continue with main and the sheet candidate to 400 Myr,
# three re-rolled draws each; two jobs at a time, 4 threads each. Store root = s260/data.
S=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/s260
W=/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-ac502a6f660c0286b
cd "${S:?}" || exit 1
export PLANET_DATA="${S:?}/data" NUMBA_NUM_THREADS=4 OMP_NUM_THREADS=4
run() { uv run --project "$W" python "${S:?}/fork_run.py" "$@"; }
SEEDS="1 77"
for s in $SEEDS; do
  run spin "${S:?}/code/main" "${S:?}/s${s}.ckpt" --seed "$s" --level 6 --fork 200 --myr 400 > "${S:?}/spin${s}.log" 2>&1 &
done
wait
jobs_list=()
for s in $SEEDS; do for code in main cand; do for d in 0 1 2; do
  jobs_list+=("$s $code $d")
done; done; done
i=0
for j in "${jobs_list[@]}"; do
  set -- $j
  off=$(python3 -c "print($3*1e-5)")
  run cont "${S:?}/code/$2" "${S:?}/s$1.ckpt" --seed "$1" --level 6 --myr 400 --offset "$off" --name "s$1_$2_d$3" \
    > "${S:?}/cont_s$1_$2_d$3.log" 2>&1 &
  i=$((i+1))
  if (( i % 2 == 0 )); then wait; fi
done
wait
echo ALLDONE
