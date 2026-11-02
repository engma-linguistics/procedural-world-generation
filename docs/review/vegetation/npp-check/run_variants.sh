#!/bin/bash
# lane 123: Earth observed-climate screens of the plant variants
cd /data/personal/repos/procedural-world-generation/.claude/worktrees/agent-aefe19dd8197a7ce6
SC=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/l123
export PLANET_DATA=/data/personal/repos/procedural-world-generation PYTHONPATH=.
while read tag args; do
  uv run python $SC/npp_check.py --tag $tag $args --json $SC/v_$tag.json 2>&1 | tail -1 &
done <<LIST
base
rl2 --herb-rl 2
eps125 --eps 1.25
rl2eps125 --herb-rl 2 --eps 1.25
rl3eps125 --herb-rl 3 --eps 1.25
LIST
wait
