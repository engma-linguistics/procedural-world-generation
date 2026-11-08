#!/bin/bash
# usage: scout2_trial.sh TAG  (env SUBCELL_K, with scout2_land_amp.patch applied; L = a scratch dir holding data/worlds/dba204.json and data/grids/L7.json) -- builds zooms A, B, C in the scratch data root and measures them
set -e
cd /data/personal/repos/procedural-world-generation/.claude/worktrees/agent-a87eb4fecb9252dc7
L=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l188
export PLANET_DATA=$L/data ZROOT=$L/data NUMBA_NUM_THREADS=3 OMP_NUM_THREADS=3
ids=""
for c in "61.3 -141.5" "10.36 69.7" "32.13 171.55"; do
  set -- $c
  id=$(uv run python -m planet zoom dba204 --lat $1 --lon $2 --size-km 1200 --res-km 4 2>&1 | grep -o 'zooms/[0-9a-f]*/' | head -1 | cut -d/ -f2)
  ids="$ids $id"
done
echo "$TAG ids:$ids" > $L/$TAG.txt
uv run python docs/review/tectonics/mountains/scout2_subcell.py $ids >> $L/$TAG.txt 2>&1
for z in $ids; do uv run python docs/review/tectonics/mountains/scout2_peaks.py $z 5 2>/dev/null | head -4 >> $L/$TAG.txt || true; done
cat $L/$TAG.txt
