#!/bin/bash
# usage: batch.sh SCRIPT < jobs    each job line: TREE SRC.pkl [k=v ...]; TREE s1 = this tree, s2 = $S2WT (step 2);
# SRC is a file in $SCR. Runs SCRIPT (scan.py or diag.py, in this directory) 8 at once, prints each job's output.
SCR=${SCR:-/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad}
export S2WT=${S2WT:-$SCR/a19_s2} SCR
export BR=$(cd "$(dirname "$0")/../../../.." && pwd)
export X=$BR/docs/review/base-climate/laneA19/$1
export NUMBA_NUM_THREADS=${NUMBA_NUM_THREADS:-3}
one() {
  t=$1; shift; s=$1; shift; d=$BR; [ "$t" = s2 ] && d=$S2WT
  out=$(cd "$d" && PYTHONPATH=.:tests uv run python "$X" "$SCR/$s" "$@" 2>&1 | grep -v "hardlink\|link-mode\|filesystems\|Installed")
  printf "%s\n" "$out" | sed "s/^/[$t] /"
}
export -f one
xargs -P 8 -L 1 bash -c 'one "$@"' _
