#!/bin/bash
# usage: launch_hot.sh THREADS OFFSET... -> the hothouse recipe (seed 16, tilt 45) at L6, 1 Gyr, star default, per offset
TH=$1; shift
W=/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-aa268f8fa4f53889e
V=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/v1f8
cd $W
for o in "$@"; do
  mkdir -p $V/hot_$o
  NUMBA_NUM_THREADS=$TH uv run python tools/ice_diag.py --seed 16 --myr 1000 --level 6 --out $V/hot_$o \
    --set tilt=45 climate_offset=$o > $V/hot_$o/log_16.txt 2>&1 &
done
wait
