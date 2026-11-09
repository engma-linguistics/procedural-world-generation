#!/bin/bash
# job.sh THREADS LOG fork_run.py-args...  (paths relative to s251; the worktree's uv env, store root = s251/data)
S=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/s251
W=/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-adabb700804b9036d
th=$1; log=$2; shift 2
cd "${S:?}" || exit 1
export PLANET_DATA="${S:?}/data" NUMBA_NUM_THREADS=$th OMP_NUM_THREADS=$th
exec uv run --project "$W" python "${S:?}/fork_run.py" "$@" > "$log" 2>&1
