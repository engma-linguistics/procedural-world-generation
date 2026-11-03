#!/bin/bash
# Lane 142: Earth screens. ec.sh TAG "TUNE overrides (k=v,k=v)": L7 earth_check and L6 moisture_regions (no cf),
# in parallel, into $S (6 threads per arm).
cd "$(dirname "$0")/../../../.." || exit 1
S=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l142
W=docs/review/base-climate/rain-supply/withtune.py
NUMBA_NUM_THREADS=4 PYTHONPATH=. uv run python $W "$2" tools/earth_check.py --level 7 --json "$S/ec_$1.json" > "$S/ec_$1.txt" 2>&1 &
NUMBA_NUM_THREADS=2 PYTHONPATH=. uv run python $W "$2" tools/moisture_regions.py --level 6 --no-cf --json "$S/mr_$1.json" > "$S/mr_$1.txt" 2>&1 &
wait
