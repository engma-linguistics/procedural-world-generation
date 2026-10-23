#!/bin/bash
# usage: [OFFS="0 0.001"] [SERIAL=1] [W=8] draws.sh tag pytest-args...
cd /data/personal/repos/procedural-world-generation/.claude/worktrees/agent-afb6b6cb29caddd7f
S=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/m1024
tag=$1; shift; offs=${OFFS:-"0 0.001 -0.001"}
for o in $offs; do
  ( start=$(date +%s); PW_SEED_OFFSET=$o PW_SEED_WORKERS=${W:-8} uv run pytest -q -rA -n 2 "$@" > $S/$tag.off$o.txt 2>&1; echo "exit $? wall $(( $(date +%s)-start )) s" >> $S/$tag.off$o.txt ) &
  if [ -n "$SERIAL" ]; then wait; fi
done
wait
