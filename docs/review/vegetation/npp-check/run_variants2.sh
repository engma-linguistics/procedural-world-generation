#!/bin/bash
# lane 123: second set of Earth observed-climate screens
cd /data/personal/repos/procedural-world-generation/.claude/worktrees/agent-aefe19dd8197a7ce6
SC=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l123
export PLANET_DATA=/data/personal/repos/procedural-world-generation PYTHONPATH=.
while read tag args; do
  uv run python $SC/npp_check.py --tag $tag $args --json $SC/v_$tag.json 2>&1 | tail -1 &
done <<LIST
rl3 --herb-rl 3
trop13 --trop-eps 1.3
rl3trop13 --herb-rl 3 --trop-eps 1.3
rl3trop15 --herb-rl 3 --trop-eps 1.5
LIST
wait
