#!/bin/bash
# usage: pr.sh TAG -> passrate over v1f7/TAG/{l6fix,l6c_0,l6c_m,l6c_p}, written to v1f7/passrate_TAG.txt
V=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/v1f7
cd /data/personal/repos/procedural-world-generation/.claude/worktrees/agent-a8c9bf545b52522e5
uv run python docs/review/base-climate/v1-finish-6/passrate.py $V/$1/l6fix $V/$1/l6c_0 $V/$1/l6c_m $V/$1/l6c_p > $V/passrate_$1.txt 2>&1
grep -E "^pooled" $V/passrate_$1.txt
grep -E "^ +l6fix" $V/passrate_$1.txt | awk '{print $3, $5}'
