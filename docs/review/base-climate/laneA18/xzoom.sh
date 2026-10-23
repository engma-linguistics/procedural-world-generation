#!/bin/bash
# Lane A16's crossing of the endings test, for step 1 vs step 2.
# usage: xzoom.sh dump | xzoom.sh zoom "TREE SRC [extra args]" ...
#   TREE / SRC: s1 = the step-1 tree ($S1WT, a detached worktree at the branch head before step 2), s2 = this tree.
SCR=${SCR:-/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad}
S1WT=${S1WT:-$SCR/a18_step1}
BR=$(cd "$(dirname "$0")/../../../.." && pwd)
X=$BR/docs/review/base-climate/laneA18/xzoom.py
tree() { [ "$1" = s1 ] && echo "$S1WT" || echo "$BR"; }
if [ "$1" = dump ]; then
  for t in s1 s2; do
    (cd "$(tree $t)" && PYTHONPATH=.:tests uv run python "$X" dump "$SCR/a18_src_$t.pkl" | sed "s#^#[$t] #") &
  done
  wait; exit
fi
shift
for a in "$@"; do
  set -- $a; t=$1; s=$2; shift 2
  (cd "$(tree $t)" && PYTHONPATH=.:tests uv run python "$X" zoom "$SCR/a18_src_$s.pkl" "$@" 2>&1 \
     | sed "s#^#[$t climate, $s world] #") &
done
wait
