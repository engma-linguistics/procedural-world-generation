#!/bin/bash
# lane 123: L6 1 Gyr sanity runs, baseline code vs candidate (herb root respiration), seeds 1 and 2, into scratch data roots
SC=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l123
WT=/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-aefe19dd8197a7ce6
cd "$WT"
(cd "$SC/base_code" && PLANET_DATA="$SC/data_base" NUMBA_NUM_THREADS=6 uv run --project "$WT" python -m planet simulate --seed 1 2 --level 6 --jobs 2 > "$SC/sim_base.log" 2>&1) &
(PLANET_DATA="$SC/data_cand" NUMBA_NUM_THREADS=6 uv run python -m planet simulate --seed 1 2 --level 6 --jobs 2 > "$SC/sim_cand.log" 2>&1) &
wait
echo done
