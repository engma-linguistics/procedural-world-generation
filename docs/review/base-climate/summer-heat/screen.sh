#!/bin/bash
# Lane 121: Earth L7 screens of the split candidates (diag.py base with TUNE overrides), 4 at once.
cd "$(dirname "$0")/../../../.." || exit 1
S=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l121/diag
for t in "" "split_lw=1" "split_bl_max=4" "split_lw=1,split_bl_max=4" "$@"; do
  PYTHONPATH=. uv run python docs/review/base-climate/summer-heat/diag.py base --tune "$t" > "$S/log_${t//[=,]/_}.txt" 2>&1 &
done
wait
