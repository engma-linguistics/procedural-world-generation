#!/bin/bash
# usage: seedscan.sh SEED...   The endings test's numbers (xzoom.py) on the L4 300 Myr run of each seed, each tree with
# its own climate (s1 = step-1 tree $S1WT, s2 = this tree), 8 processes at once. One line per (tree, seed).
SCR=${SCR:-/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad}
export S1WT=${S1WT:-$SCR/a18_step1} SCR
export BR=$(cd "$(dirname "$0")/../../../.." && pwd)
export X=$BR/docs/review/base-climate/laneA18/xzoom.py
one() {
  t=$1; s=$2; d=$BR; [ "$t" = s1 ] && d=$S1WT
  cd "$d" || exit
  a=$(PYTHONPATH=.:tests uv run python "$X" dump "$SCR/a18_src_${t}_$s.pkl" "$s" 2>/dev/null | grep dumped)
  b=$(PYTHONPATH=.:tests uv run python "$X" zoom "$SCR/a18_src_${t}_$s.pkl" 2>/dev/null | grep ending | sed 's/^.*\]: //')
  echo "$t seed $s | $a | $b"
}
export -f one
for s in "$@"; do echo "s1 $s"; echo "s2 $s"; done | xargs -P 8 -L 1 bash -c 'one $0 $1'
