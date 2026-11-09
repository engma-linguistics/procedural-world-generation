#!/bin/bash
# bench.sh MYR CODE...: bench.py on the L7 seed 11 fork for each code, one after another, 4 threads
S=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/s251
W=/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-adabb700804b9036d
cd "${S:?}" || exit 1
export NUMBA_NUM_THREADS=4 OMP_NUM_THREADS=4
myr=$1; shift
for c in "$@"; do
  uv run --project "$W" python "${S:?}/bench.py" "code/$c" fork/s11_L7_at200.ckpt 11 7 "$myr" 2>&1 | grep -v -i warn
done
