#!/bin/bash
# usage: launch_never.sh THREADS RATE... -> v1-finish-7's three never-ice L6 draws (583167 and 957317 at offset 0,
# 53669 at +0.001), 1 Gyr, at each star_brightening RATE (code path, ice_diag); outputs in v1f8/nv_<rate>
TH=$1; shift
W=/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-aa268f8fa4f53889e
V=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/v1f8
cd $W
for r in "$@"; do
  mkdir -p $V/nv_$r
  for so in 583167:0 957317:0 53669:0.001; do
    s=${so%%:*}; o=${so##*:}
    NUMBA_NUM_THREADS=$TH uv run python tools/ice_diag.py --seed $s --myr 1000 --level 6 --out $V/nv_$r \
      --set climate_offset=$o star_brightening=$r > $V/nv_$r/log_$s.txt 2>&1 &
  done
done
wait
