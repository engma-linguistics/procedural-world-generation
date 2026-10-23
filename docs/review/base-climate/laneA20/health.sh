#!/bin/bash
# usage: health.sh   tools/health.py --quick on main 59b83d7 ($MAINWT, a detached worktree) and on this branch,
# 2 workers x 2 threads each (4 runs at once while the L7 builds run). Reports in laneA20/health_{main,branch}/.
here="$(cd "$(dirname "$0")/../../../.." && pwd)"
o=$here/docs/review/base-climate/laneA20
MAINWT=${MAINWT:-/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/a20_main}
(cd "$MAINWT" && uv run python tools/health.py --quick --workers 2 --threads 2 --out "$o/health_main" > "$o/health_main.log" 2>&1) &
(cd "$here" && uv run python tools/health.py --quick --workers 2 --threads 2 --out "$o/health_branch" > "$o/health_branch.log" 2>&1) &
wait
