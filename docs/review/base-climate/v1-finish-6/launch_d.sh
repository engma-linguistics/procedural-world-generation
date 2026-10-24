#!/bin/bash
# usage: launch_d.sh TAG THREADS "k=v ..."   -> the 18 L6 seed-draws with option D (d_run.py)
TAG=$1; TH=$2; EXTRA=$3; W=/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-a887b48c43cf726e8
V=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/v1f6
OUT=$V/$TAG
cd $W
run() { mkdir -p $OUT/$1; NUMBA_NUM_THREADS=$TH uv run python $V/d_run.py $2 $OUT/$1 climate_offset=$3 $EXTRA > $OUT/$1/log_$2.txt 2>&1 & }
for s in 957317 619496 583167 639472; do run l6fix $s 0; done
for s in 53669 733847 819014 958504; do run l6c_0 $s 0; done
for s in 53669 958504; do run l6c_m $s -0.001; done
for s in 53669 583167 619496 639472 733847 819014 957317 958504; do run l6c_p $s 0.001; done
wait
