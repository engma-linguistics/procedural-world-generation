#!/bin/bash
# examples.sh: L6 1 Gyr example runs into the main checkout's store, main code vs branch code, seeds 1 2.
# Gated like paired.sh (at most 8 sims machine-wide, 40 GB free).
S=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l23
export PLANET_DATA=/home/daniel/personal/repos/procedural-world-generation
nsim() { ps -eo args | grep -E "python3? (tools/ice_diag.py|-m planet simulate|\S*riftdiag.py|\S*crustdiag.py|\S*diag.py|\S*/wl.py)" | grep -v -E "^(/home/daniel/.local/bin/)?uv " | grep -v grep | wc -l; }
pids=()
for job in "main 1" "new 1" "main 2" "new 2"; do
  set -- $job
  [ "$1" = main ] && W=$S/mainsrc || W=$S/newsrc
  while [ $(nsim) -ge 8 ] || [ $(free -g | awk "/^Mem/{print \$7}") -lt 40 ]; do sleep 20; done
  echo "$(date +%H:%M) start crust-$1-s$2"
  (cd $W && NUMBA_NUM_THREADS=5 nohup uv run python -m planet simulate --seed $2 --level 6 --myr 1000 \
     --name crust-$1-s$2 > $S/ex_$1_s$2.log 2>&1 < /dev/null) &
  pids+=($!)
  sleep 40
done
for p in "${pids[@]}"; do wait $p; done
echo "$(date +%H:%M) examples done"
