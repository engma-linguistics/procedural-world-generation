#!/bin/bash
# usage: launch_ww.sh THREADS MYR TAG SET... -> the water-world recipe (seed 13) at L6, draws at offset 0 and +0.001,
# with extra --set overrides (e.g. star_brightening=0 for the star-off reference); outputs in v1f8/TAG_<offset>
TH=$1; M=$2; TAG=$3; shift 3
W=/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-aa268f8fa4f53889e
V=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/v1f8
cd $W
for o in 0 0.001; do
  mkdir -p $V/${TAG}_$o
  NUMBA_NUM_THREADS=$TH uv run python tools/ice_diag.py --seed 13 --myr $M --level 6 --out $V/${TAG}_$o \
    --set continental_start=0.1 heat_start=2 climate_offset=$o "$@" > $V/${TAG}_$o/log_13.txt 2>&1 &
done
wait
