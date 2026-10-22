#!/bin/bash
# usage: rd.sh tag [ENV=..]...  -> out/d_tag.txt
cd /data/personal/repos/procedural-world-generation/.claude/worktrees/agent-abbf08ba762366c44 || exit 1
S=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/laneA11
tag=$1; shift
env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMBA_NUM_THREADS=${NT:-4} "$@" uv run python $S/endiag.py $tag > $S/out/d_$tag.txt 2>&1
