#!/bin/bash
# usage: [TH=2] [P=10] [SCRIPT=...] diag.sh OUTNAME "SEEDS" [ice_diag args, e.g. --set climate_offset=0.001]
# ice_diag-like SCRIPT (default this folder's relief.py) at L6 over 1 Gyr on each seed from this worktree, P at once,
# TH numba threads each, into $V/OUTNAME/, then the summary into summary.txt.
V=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/v1f2
ROOT=/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-a88a4faf3662fcb21
name=$1; seeds=$2; shift 2
out=$V/$name
mkdir -p $out
cd $ROOT
running=0
for s in $seeds; do
  NUMBA_NUM_THREADS=${TH:-2} uv run python ${SCRIPT:-docs/review/base-climate/v1-finish-2/relief.py} --seed $s --out $out "$@" > $out/seed$s.log 2>&1 &
  running=$((running + 1))
  if [ $running -ge ${P:-10} ]; then wait -n; running=$((running - 1)); fi
done
wait
uv run python tools/ice_diag.py --summary $out/seed*_L6.json.gz > $out/summary.txt 2>&1
