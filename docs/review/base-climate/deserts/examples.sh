#!/bin/bash
# usage: examples.sh SCRATCH -> L6 1 Gyr example runs into the main checkout's store, seeds 1 2: main code
# (SCRATCH/code/main) as desert-main-sN and the branch code (SCRATCH/code/r1) as desert-new-sN. Lane 25 (PW-015).
L=$1
PY=$(cd "$(dirname "$0")/../../../.." && pwd)/.venv/bin/python
export PLANET_DATA=/home/daniel/personal/repos/procedural-world-generation
pids=()
for job in "main 1" "new 1" "main 2" "new 2"; do
  set -- $job
  [ "$1" = main ] && C=$L/code/main || C=$L/code/r1
  (cd "$C" && NUMBA_NUM_THREADS=3 "$PY" -m planet simulate --seed "$2" --level 6 --myr 1000 --name "desert-$1-s$2" \
     > "$L/ex_$1_s$2.log" 2>&1 < /dev/null) &
  pids+=($!)
  sleep 5
done
for p in "${pids[@]}"; do wait "$p"; done
echo "examples done"
