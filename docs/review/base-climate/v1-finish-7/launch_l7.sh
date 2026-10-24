#!/bin/bash
# usage: launch_l7.sh TAG THREADS OFFSET -> the 4 showcase seeds at L7, 1 Gyr, with the code's default star
# (star_brightening 0.45), through tools/ice_diag.py; outputs in v1f7/TAG
TAG=$1; TH=$2; OFF=$3
W=/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-a8c9bf545b52522e5
V=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/v1f7
mkdir -p $V/$TAG
cd $W
for s in 957317 619496 583167 639472; do
  NUMBA_NUM_THREADS=$TH uv run python tools/ice_diag.py --seed $s --myr 1000 --level 7 --out $V/$TAG \
    --set climate_offset=$OFF > $V/$TAG/log_$s.txt 2>&1 &
done
wait
