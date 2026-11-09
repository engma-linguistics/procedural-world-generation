#!/bin/bash
# Scout 232 (PW-1518): Earth screens of the diffuse-light gain (probe.py), two at a time x 4 threads.
# Run from the worktree root; needs a real data/earth copy there (not a symlink). Args: name "flags" pairs.
set -u
OUT=docs/review/climate/diffuse/out
mkdir -p "$OUT"
export PLANET_DATA=/data/personal/repos/procedural-world-generation NUMBA_NUM_THREADS=4
while [ $# -ge 4 ]; do
  # shellcheck disable=SC2086
  uv run python docs/review/climate/diffuse/probe.py $2 > "$OUT/$1.txt" 2>&1 &
  # shellcheck disable=SC2086
  uv run python docs/review/climate/diffuse/probe.py $4 > "$OUT/$3.txt" 2>&1
  wait
  shift 4
done
if [ $# -ge 2 ]; then
  # shellcheck disable=SC2086
  uv run python docs/review/climate/diffuse/probe.py $2 > "$OUT/$1.txt" 2>&1
fi
