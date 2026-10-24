#!/bin/bash
# usage: launch_l7.sh THREADS -> two L7 2 Gyr draws on the code default star (0.45): Earth-like B's seed 12 and
# showcase seed 619496 (v1-finish-7's one L7 fail), climate_offset 0; outputs in v1f8/l7_2g
TH=$1
W=/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-aa268f8fa4f53889e
V=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/v1f8
mkdir -p $V/l7_2g
cd $W
for s in 12 619496; do
  NUMBA_NUM_THREADS=$TH uv run python tools/ice_diag.py --seed $s --myr 2000 --level 7 --out $V/l7_2g \
    --set climate_offset=0 > $V/l7_2g/log_$s.txt 2>&1 &
done
wait
