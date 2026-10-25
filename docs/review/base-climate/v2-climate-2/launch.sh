#!/bin/bash
# usage: launch.sh BATCH THREADS -> one batch of v2-climate-2's ice_diag runs (PW-798), in the foreground (waits);
# outputs in the session scratchpad v2c2/<tag>/seed<N>_L<l>.json.gz.
#   ww6   the water world (seed 13), L6 2 Gyr, three draws (offset 0 / +0.001 / -0.001)
#   el1-3 v1-finish-5's 18 Earth-like L6 1 Gyr seed-draws (code default), six per batch
#   ww7   the water world at L7, 2 Gyr, two draws
B=$1; TH=$2
W=/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-af6c091bd3379671c
V=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/v2c2
cd $W
run() {  # tag level myr seed sets...
  local tag=$1 l=$2 m=$3 s=$4; shift 4
  mkdir -p $V/$tag
  NUMBA_NUM_THREADS=$TH uv run python tools/ice_diag.py --seed $s --myr $m --level $l --out $V/$tag --set "$@" \
    > $V/$tag/log_${s}_L$l.txt 2>&1 &
}
WW="continental_start=0.1 heat_start=2"
case $B in
  ww6) for o in 0 0.001 -0.001; do run ww_$o 6 2000 13 $WW climate_offset=$o; done ;;
  el1) for s in 957317 619496 583167 639472; do run l6fix 6 1000 $s climate_offset=0; done
       for s in 53669 733847; do run l6c_0 6 1000 $s climate_offset=0; done ;;
  el2) for s in 819014 958504; do run l6c_0 6 1000 $s climate_offset=0; done
       for s in 53669 958504; do run l6c_m 6 1000 $s climate_offset=-0.001; done
       for s in 53669 583167; do run l6c_p 6 1000 $s climate_offset=0.001; done ;;
  el3) for s in 619496 639472 733847 819014 957317 958504; do run l6c_p 6 1000 $s climate_offset=0.001; done ;;
  ww7) for o in 0 0.001; do run ww_$o 7 2000 13 $WW climate_offset=$o; done ;;
  # v1 sign-off (PW-780): Earth-like code default, 2 Gyr
  s6) run so6 6 2000 11 climate_offset=0; run so6 6 2000 21 climate_offset=0; run so6p 6 2000 957317 climate_offset=0.001 ;;
  s6b) for s in 583167 619496 639472; do run so6p 6 2000 $s climate_offset=0.001; done ;;
  s7) run so7 7 2000 957317 climate_offset=0 ;;
esac
wait
