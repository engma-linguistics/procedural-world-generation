#!/bin/bash
# usage: runp3.sh OUTDIR "belt col" ...   (lane A15's stage-3 probe per X_BELT / X_COL variant, in parallel)
cd "$(dirname "$0")/../../../.."
out=$1; shift
mkdir -p "$out"
for v in "$@"; do
  read -r b c x y <<< "$v"; set -- "" "" "$x" "$y"
  X_BELT=$b X_COL=$c uv run python docs/review/base-climate/laneA15/p3.py "$3" > "$out/p3_b${b}_c${c}$4.txt" 2>&1 &
done
wait
