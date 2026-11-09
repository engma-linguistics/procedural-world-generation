#!/bin/bash
cd "/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/s261" || exit 1
export PLANET_DATA="/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/s261/data" NUMBA_NUM_THREADS=4 OMP_NUM_THREADS=4
for s in 1 77; do
  uv run --project "/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-ac502a6f660c0286b" python "/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/s261/fork_run.py" spin "/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/s261/code/main" "/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/s261/s$s.ckpt" --seed $s --level 6 --fork 200 --myr 400 > "/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/s261/spin$s.log" 2>&1 &
done
wait
echo SPINDONE
