#!/bin/bash
# Lane 132: the SST-swap diagnostic screens. swap.sh TAG SPEC (sstswap.py's DT[:LAT0:LAT1]) ["TUNE overrides"]
cd "$(dirname "$0")/../../../.." || exit 1
S=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l132
D=docs/review/base-climate/rain-supply
PYTHONPATH=. uv run python $D/withtune.py "${3:-}" $D/sstswap.py "$2" tools/earth_check.py --level 7 > "$S/ec_$1.txt" 2>&1 &
PYTHONPATH=. uv run python $D/withtune.py "${3:-}" $D/sstswap.py "$2" docs/review/base-climate/tropical-cloud/screen.py > "$S/cl_$1.txt" 2>&1 &
PYTHONPATH=. uv run python $D/withtune.py "${3:-}" $D/sstswap.py "$2" tools/moisture_regions.py --level 6 --no-cf > "$S/mr_$1.txt" 2>&1 &
wait
