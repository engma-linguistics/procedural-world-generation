#!/bin/bash
# run_all.sh OUT [JOBS]: the dragon-numbers probe in one command, from the repository root, on the code checked out.
# Runs census.py (docs/review/megafauna/probe.py plus the census) on the six probe worlds at roll 7000, in two arms: "on" (the model)
# and "nosea" (the sea food, D28 B, off), JOBS at a time (default 4) with NUMBA_NUM_THREADS=2, then tables.py into OUT.
# Each run takes ~35-95 min on a shared machine; the twelve ~3-5 h at 4 jobs. tables.py reads the first arm (nosea, the code as
# main had it before D28 B) for the per-kind and chart numbers, and compares "on" against it. Needs the six worlds (PLANET_DATA, or the repository).
# Re-run after a peoples-model merge (lane 97) to refresh every number in report.md; the tables land in OUT/tables.md.
set -euo pipefail
OUT=${1:?usage: run_all.sh OUT [JOBS]}
JOBS=${2:-4}
mkdir -p "$OUT/on" "$OUT/nosea"
for w in 2a7385 1df1c3 e71172 6909cb a12762 067778; do
  echo "$w on"
  echo "$w nosea"
done | xargs -P "$JOBS" -n 2 sh -c '
  arm=$1; w=$0; flag=""; [ "$arm" = nosea ] && flag="--no-sea"
  NUMBA_NUM_THREADS=2 uv run python docs/review/dragon-numbers/census.py "$w" 7000 "'"$OUT"'/$arm" $flag > "'"$OUT"'/$arm/$w.log" 2>&1'
uv run --with matplotlib python docs/review/dragon-numbers/tables.py "$OUT" nosea="$OUT/nosea" on="$OUT/on"
