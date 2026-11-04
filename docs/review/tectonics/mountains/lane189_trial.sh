#!/bin/bash
# usage: trial.sh TAG CODE_DIR [K]  -- builds 3 zooms of world 899985 (1200 km, 4 km/px) with CODE_DIR's planet, in its
# own scratch data root, and measures them
set -e
S=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l189
TAG=$1; CODE=$2
D=$S/d_$TAG
mkdir -p $D/worlds $D/grids
cp -n $S/data/worlds/899985.json $S/data/worlds/899985.txt $D/worlds/
cp -n $S/data/grids/L7.json $D/grids/
export PLANET_DATA=$D NUMBA_NUM_THREADS=3 OMP_NUM_THREADS=3
[ -n "$3" ] && export SUBCELL_K=$3
PY=/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-a426aa86233ddf6f4/.venv/bin/python
cd $CODE
ids=""
for c in "-37.5 -143" "-37.0 176.8" "47.77 22.13"; do
  set -- $c
  id=$(PYTHONPATH=$CODE $PY -m planet zoom 899985 --lat=$1 --lon=$2 --size-km 1200 --res-km 4 2>&1 | grep -o 'zooms/[0-9a-f]*/' | head -1 | cut -d/ -f2)
  ids="$ids $id"
done
echo "$TAG ids:$ids" > $S/$TAG.txt
cd /data/personal/repos/procedural-world-generation/.claude/worktrees/agent-a426aa86233ddf6f4
ZROOT=$D $PY docs/review/tectonics/mountains/lane189_measure.py $ids >> $S/$TAG.txt 2>&1
cat $S/$TAG.txt
