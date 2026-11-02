#!/bin/bash
# Lane 121: tools/earth_check.py --level 7 for main and the arms (private data/earth copy in the worktree).
cd "$(dirname "$0")/../../../.." || exit 1
S=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l121/ec
mkdir -p "$S"
for t in "" "split_bl_max=4" "split_lw=1,split_bl_max=4"; do
  tag="main${t:+_${t//[=,]/_}}"
  PYTHONPATH=. uv run python docs/review/base-climate/rain-inland/withtune.py "$t" tools/earth_check.py --level 7 \
    --json "$S/$tag.json" > "$S/$tag.txt" 2>&1 &
done
wait
