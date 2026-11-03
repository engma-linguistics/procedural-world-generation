#!/bin/bash
# Lane 150: sc.sh TAG [k=v ...] -> screen.py on Earth L6 into $S/sc_TAG.txt (4 threads)
cd "$(dirname "$0")/../../../.." || exit 1
S=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l150
tag=$1
shift
NUMBA_NUM_THREADS=4 uv run python docs/review/base-climate/nordic-seas/screen.py "$S/obs/sst.ltm.1991-2020.nc" "$@" \
  > "$S/sc_$tag.txt" 2>&1
