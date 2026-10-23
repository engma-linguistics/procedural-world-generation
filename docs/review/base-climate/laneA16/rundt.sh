#!/bin/bash
# usage: rundt.sh SEED   (the run under 6 hash seeds and one random, in parallel)
cd "$(dirname "$0")/../../../.."
for h in 0 1 2 3 4 5; do
  PYTHONHASHSEED=$h NUMBA_NUM_THREADS=4 PYTHONPATH=.:tests uv run python docs/review/base-climate/laneA16/rundt.py $1 2>/dev/null &
done
NUMBA_NUM_THREADS=4 PYTHONPATH=.:tests uv run python docs/review/base-climate/laneA16/rundt.py $1 2>/dev/null &
wait
