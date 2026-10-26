#!/bin/bash
# usage: pr.sh PREFIX [WAIT_N] -> (after waiting up to ~9.5 min for WAIT_N result files) passrate3.py on every
# v1f11/<PREFIX>_* sweep dir, condensed.
V=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/v1f11
W=/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-a179403626d26ae3e
N=${2:-0}
for i in $(seq 1 57); do [ $(ls $V/$1_*/seed*.json.gz 2>/dev/null | wc -l) -ge $N ] && break; sleep 10; done
echo "files: $(ls $V/$1_*/seed*.json.gz 2>/dev/null | wc -l)"
cd $W && uv run python docs/review/base-climate/v1-finish-11/passrate3.py $V/$1_* 2>&1 | grep -v Warning
