#!/bin/bash
# Lane 132: Earth screens. ec.sh TAG "TUNE overrides": L7 earth_check, lane 126's cloud/sunshine screen (L7) and
# L6 moisture_regions (no cf), in parallel, into $S.
cd "$(dirname "$0")/../../../.." || exit 1
S=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l132
mkdir -p "$S"
W=docs/review/base-climate/rain-supply/withtune.py
PYTHONPATH=. uv run python $W "$2" tools/earth_check.py --level 7 --json "$S/ec_$1.json" > "$S/ec_$1.txt" 2>&1 &
PYTHONPATH=. uv run python $W "$2" docs/review/base-climate/tropical-cloud/screen.py --save "$S/cl_$1.npz" > "$S/cl_$1.txt" 2>&1 &
PYTHONPATH=. uv run python $W "$2" tools/moisture_regions.py --level 6 --no-cf --json "$S/mr_$1.json" > "$S/mr_$1.txt" 2>&1 &
wait
