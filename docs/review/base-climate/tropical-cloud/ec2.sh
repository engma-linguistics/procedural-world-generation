#!/bin/bash
# Lane 131: Earth L7 screen arm: ec2.sh TAG "TUNE overrides"; screen2.py and earth_check.py in parallel.
cd "$(dirname "$0")/../../../.." || exit 1
S=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l131
mkdir -p "$S"
PYTHONPATH=. uv run python docs/review/base-climate/tropical-cloud/withtune.py "$2" \
  docs/review/base-climate/tropical-cloud/screen2.py --save "$S/$1.npz" > "$S/$1.txt" 2>&1 &
PYTHONPATH=. uv run python docs/review/base-climate/tropical-cloud/withtune.py "$2" tools/earth_check.py --level 7 \
  --json "$S/ec_$1.json" > "$S/ec_$1.txt" 2>&1 &
wait
