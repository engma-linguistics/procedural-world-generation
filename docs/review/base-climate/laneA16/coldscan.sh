#!/bin/bash
# usage: [FROM=25 TO=35] coldscan.sh TREE OUT   (the cold_moment fixture's seeds, one process per seed, in TREE)
X=$(cd "$(dirname "$0")" && pwd)/coldscan.py
cd "$1"
for s in $(seq ${FROM:-25} ${TO:-35}); do
  PYTHONPATH=.:tests NUMBA_NUM_THREADS=1 uv run python "$X" $s 2>/dev/null &
done > "$2"
wait
sort -k2 -n "$2" -o "$2"
