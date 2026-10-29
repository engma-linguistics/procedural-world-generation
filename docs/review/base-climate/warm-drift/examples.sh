#!/bin/bash
# L6 1 Gyr example runs into the main checkout's store: main code (l24/main) vs branch code (l24/b1), seeds 1 2.
L=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l24
PY=/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-a593a386fec489ab4/.venv/bin/python
export PLANET_DATA=/home/daniel/personal/repos/procedural-world-generation
pids=()
for job in "main 1" "new 1" "main 2" "new 2"; do
  set -- $job
  [ "$1" = main ] && C=$L/main || C=$L/b1
  (cd $C && NUMBA_NUM_THREADS=4 $PY -m planet simulate --seed $2 --level 6 --myr 1000 --name warm-$1-s$2 \
     > $L/ex_$1_s$2.log 2>&1 < /dev/null) &
  pids+=($!)
  sleep 5
done
for p in "${pids[@]}"; do wait $p; done
echo "examples done"
