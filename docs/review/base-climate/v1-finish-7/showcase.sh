#!/bin/bash
# usage: showcase.sh THREADS -> the v1 L7 showcase on the 4 seeds (planet make --level 7, earthlike, 1 Gyr, 300 kyr
# time zoom, now = interglacial, 4 zooms, resources), into the main checkout's data root; logs in v1f7/showcase/
TH=$1
W=/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-a8c9bf545b52522e5
V=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/v1f7/showcase
mkdir -p $V
cd $W
for s in 957317 619496 583167 639472; do
  PLANET_DATA=/data/personal/repos/procedural-world-generation NUMBA_NUM_THREADS=$TH \
    uv run python -m planet make --level 7 --seed $s > $V/make_$s.txt 2>&1 &
done
wait
