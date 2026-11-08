#!/bin/bash
# PW-1497 scout 209 screens (needs scout6_andean.patch applied: git apply docs/review/tectonics/mountains/scout6_andean.patch): arms x L6 seeds x MYR, one process per arm (3 threads each), runs under exports/data/runs.
# usage: scout6_screen.sh MYR "SEEDS" ARM:SHARE:MODE ...   e.g. scout6_screen.sh 600 "1 2 6001" main:0:thermo t05:0.5:thermo
cd "$(dirname "$0")/../../../.." || exit 1
export PLANET_DATA=$PWD/exports/data
MYR=$1; SEEDS=$2; shift 2
for spec in "$@"; do
  IFS=: read -r ARM SHARE MODE <<< "$spec"
  NUMBA_NUM_THREADS=3 uv run python -m planet simulate --seed $SEEDS --level 6 --myr "$MYR" --jobs 1 --threads 3 \
    --name "s209_$ARM" --set andean_shortening="$SHARE" andean_mode="$MODE" > "exports/log_$ARM.txt" 2>&1 &
done
wait
echo "all done"
