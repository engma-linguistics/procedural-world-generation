#!/bin/bash
# usage: xzoom.sh dump | xzoom.sh zoom "ARGS1" "ARGS2" ...
#   dump: sim4's source from main's tree ($MAINWT) and the branch's into $SCR/src_{main,branch}.pkl
#   zoom: each ARGS is "TREE SRC [belt1] [col1]" (TREE main|branch, SRC main|branch), run in parallel
SCR=${SCR:-/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad}
MAINWT=${MAINWT:-$SCR/mainwt}
BR=$(cd "$(dirname "$0")/../../../.." && pwd)
X=$BR/docs/review/base-climate/laneA16/xzoom.py
tree() { [ "$1" = main ] && echo "$MAINWT" || echo "$BR"; }
if [ "$1" = dump ]; then
  (cd "$MAINWT" && PYTHONPATH=.:tests uv run python "$X" dump "$SCR/src_main.pkl") &
  (cd "$BR" && PYTHONPATH=.:tests uv run python "$X" dump "$SCR/src_branch.pkl") &
  wait; exit
fi
shift
for a in "$@"; do
  set -- $a
  t=$1; s=$2; shift 2
  (cd "$(tree $t)" && PYTHONPATH=.:tests uv run python "$X" zoom "$SCR/src_$s.pkl" "$@" 2>&1 | sed "s#^#[$t climate] #") &
done
wait
