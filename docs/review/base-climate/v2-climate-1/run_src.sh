#!/bin/bash
# usage: run_src.sh TAG SEED MYR LEVEL SET...  -> srcdiag into v2c1/TAG.json
W=/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-a322772a3ede515e6
V=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/v2c1
TAG=$1; SEED=$2; MYR=$3; L=$4; shift 4
cd $W
NUMBA_NUM_THREADS=${TH:-4} uv run python $V/srcdiag.py $W $SEED $MYR $L $V/$TAG.json "$@" > $V/$TAG.log 2>&1
