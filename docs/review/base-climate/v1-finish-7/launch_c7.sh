#!/bin/bash
# usage: launch_c7.sh TAG THREADS [LAM] [RATE] -> the 18 L6 seed-draws (v1-finish-5's) with C' (c7_run.py), measurement only
TAG=$1; TH=$2; L=${3:-}; R=${4:-}
W=/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-a8c9bf545b52522e5
V=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/v1f7
OUT=$V/$TAG
cd $W
run() {
  mkdir -p $OUT/$1
  if [ -n "$L" ]; then export LAM=$L; fi
  if [ -n "$R" ]; then export RATE=$R; fi
  NUMBA_NUM_THREADS=$TH uv run python docs/review/base-climate/v1-finish-7/c7_run.py $2 $OUT/$1 climate_offset=$3 \
    > $OUT/$1/log_$2.txt 2>&1 &
}
for s in 957317 619496 583167 639472; do run l6fix $s 0; done
for s in 53669 733847 819014 958504; do run l6c_0 $s 0; done
for s in 53669 958504; do run l6c_m $s -0.001; done
for s in 53669 583167 619496 639472 733847 819014 957317 958504; do run l6c_p $s 0.001; done
wait
