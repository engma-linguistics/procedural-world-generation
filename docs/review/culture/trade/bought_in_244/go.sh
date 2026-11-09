#!/bin/bash
# usage: go.sh tag [KEY=VAL ...]: the four runs in parallel, one thread each; waits for all
L=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l244
W=/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-a9ca3db94d786ae10
tag=$1; shift
cd "$W" || exit 1
pids=()
for r in 3e0eb4 a24559 1e97dd 07c755; do
  PYTHONPATH=$W PLANET_DATA=$L/data NUMBA_NUM_THREADS=1 OMP_NUM_THREADS=1 uv run python "$L/h.py" "$r" "$tag" "$@" > "$L/out/log-$tag-$r.txt" 2>&1 &
  pids+=($!)
done
echo "pids ${pids[*]}"
for p in "${pids[@]}"; do tail --pid="$p" -f /dev/null; done
grep -h "done\|Error\|Traceback" "$L"/out/log-"$tag"-*.txt
