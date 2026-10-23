#!/bin/bash
# usage: [TH=2] [P=4] diag.sh TREE "SEEDS" [--set k=v ...] -- tools/ice_diag.py (L6, 1 Gyr) on each seed, P at once,
# TH numba threads each, into $T/diag_<tree><SUFFIX>/; then the 10-seed summary into summary.txt
T=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/t1024
tree=$1; seeds=$2; shift 2
name=$(basename $tree)${SUFFIX}
case $tree in /*) dir=$tree ;; *) dir=$T/$tree ;; esac
out=$T/diag_$name
mkdir -p $out
cd $dir
running=0
for s in $seeds; do
  NUMBA_NUM_THREADS=${TH:-2} uv run python tools/ice_diag.py --seed $s --out $out "$@" > $out/seed$s.log 2>&1 &
  running=$((running + 1))
  if [ $running -ge ${P:-4} ]; then wait -n; running=$((running - 1)); fi
done
wait
uv run python tools/ice_diag.py --summary $out/seed*_L6.json.gz > $out/summary.txt 2>&1
