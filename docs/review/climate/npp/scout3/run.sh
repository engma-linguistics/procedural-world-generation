#!/bin/bash
# Scout 217: Earth screens of TrBE's respiration and efficiency (scout3_probe.py), 6 variants x 2 threads.
# Run from the worktree root; needs a real data/earth copy there (not a symlink).
set -u
OUT=docs/review/climate/npp/scout3
export PLANET_DATA=/data/personal/repos/procedural-world-generation NUMBA_NUM_THREADS=2
run() { local name=$1; shift; uv run python docs/review/climate/npp/scout3_probe.py "$@" > "$OUT/$name.txt" 2>&1; }
run main &
run rl1.5 --rl-x 1.5 &
run rl2.0 --rl-x 2.0 &
run rw1.5 --rw-x 1.5 &
run rl1.5_eps1.076 --rl-x 1.5 --eps-x 1.076 &
run rl2.0_eps1.153 --rl-x 2.0 --eps-x 1.153 &
wait
