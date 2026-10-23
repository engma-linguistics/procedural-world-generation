#!/bin/bash
# usage: xcold.sh dump SEED...   (each seed's L5 source from main's tree and the branch's: $SCR/l5_{main,branch}_SEED.pkl)
#        xcold.sh cold "TREE SRC_TREE SEED [belt1] [col1]" ...   (in parallel)
SCR=${SCR:-/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad}
MAINWT=${MAINWT:-$SCR/mainwt}
BR=$(cd "$(dirname "$0")/../../../.." && pwd)
X=$BR/docs/review/base-climate/laneA16/xcold.py
tree() { [ "$1" = main ] && echo "$MAINWT" || echo "$BR"; }
mode=$1; shift
if [ "$mode" = dump ]; then
  for s in "$@"; do for t in main branch; do
    (cd "$(tree $t)" && PYTHONPATH=.:tests NUMBA_NUM_THREADS=2 uv run python "$X" dump $s "$SCR/l5_${t}_$s.pkl" 2>/dev/null) &
  done; done
  wait; exit
fi
for a in "$@"; do
  set -- $a
  t=$1; st=$2; s=$3; shift 3
  (cd "$(tree $t)" && PYTHONPATH=.:tests NUMBA_NUM_THREADS=2 uv run python "$X" cold "$SCR/l5_${st}_$s.pkl" "$@" 2>/dev/null | sed "s#^#[$t climate] #") &
done
wait
