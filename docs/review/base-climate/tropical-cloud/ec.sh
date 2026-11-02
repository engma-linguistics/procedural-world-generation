#!/bin/bash
# Lane 126: Earth L7 screens. ec.sh TAG "TUNE overrides" [earth_check too: 1]; screen.py and earth_check.py in parallel.
cd "$(dirname "$0")/../../../.." || exit 1
S=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l126
mkdir -p "$S"
PYTHONPATH=. uv run python docs/review/base-climate/tropical-cloud/withtune.py "$2" \
  docs/review/base-climate/tropical-cloud/screen.py --save "$S/$1.npz" > "$S/$1.txt" 2>&1 &
if [ "${3:-0}" = 1 ]; then
  PYTHONPATH=. uv run python docs/review/base-climate/tropical-cloud/withtune.py "$2" tools/earth_check.py --level 7 \
    --json "$S/ec_$1.json" > "$S/ec_$1.txt" 2>&1 &
fi
wait
