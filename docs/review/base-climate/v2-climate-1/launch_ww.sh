#!/bin/bash
# usage: launch_ww.sh THREADS MYR LEVEL OFFSET... -> the water-world recipe (seed 13, code default star) at each
# climate_offset, through ice_diag; outputs in v2c1/ww_L<level>_<offset>
TH=$1; M=$2; L=$3; shift 3
W=/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-a322772a3ede515e6
V=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/v2c1
cd $W
for o in "$@"; do
  mkdir -p $V/ww_L${L}_$o
  NUMBA_NUM_THREADS=$TH uv run python tools/ice_diag.py --seed 13 --myr $M --level $L --out $V/ww_L${L}_$o \
    --set continental_start=0.1 heat_start=2 climate_offset=$o > $V/ww_L${L}_$o/log_13.txt 2>&1 &
done
wait
