#!/bin/bash
# usage: launch.sh THREADS -> v1-finish-8's L6 sweep with the code default star (0.45), through tools/ice_diag.py;
# outputs in the session scratchpad v1f8/<tag>/seed<N>_L6.json.gz. One dir per (recipe, draw).
TH=$1
W=/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-aa268f8fa4f53889e
V=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/v1f8
cd $W
run() {  # tag seed myr set...
  local tag=$1 s=$2 m=$3; shift 3
  mkdir -p $V/$tag
  NUMBA_NUM_THREADS=$TH uv run python tools/ice_diag.py --seed $s --myr $m --level 6 --out $V/$tag --set "$@" \
    > $V/$tag/log_$s.txt 2>&1 &
}
# 2 Gyr: water world (seed 13), Earth-like B (seed 12, recipe 1500, run to 2000), showcase seeds at default
for o in 0 0.001 -0.001; do run ww_$o 13 2000 continental_start=0.1 heat_start=2 climate_offset=$o; done
for o in 0 0.001 -0.001; do run eb_$o 12 2000 climate_offset=$o; done
for s in 957317 619496 583167 639472; do run sc2g $s 2000 climate_offset=0; done
# cold / hothouse recipes (1 Gyr), star on (2 draws) and star off (reference)
for o in -6 -6.001; do run cold_$o 15 1000 tilt=15 climate_offset=$o; done
for o in 5 5.001; do run hot_$o 16 1000 tilt=45 climate_offset=$o; done
run cold_nostar 15 1000 tilt=15 climate_offset=-6 star_brightening=0
run hot_nostar 16 1000 tilt=45 climate_offset=5 star_brightening=0
wait
