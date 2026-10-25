#!/bin/bash
# usage: before_after.sh ROOT out [runs...]   (ROOT: the planet package's parent dir)
R=$1; O=$2; shift 2
RUNS=${@:-"-1:0 350:0 280:0 180:0"}
for w in 6fbc2c a12762 067778 6909cb e71172 2a7385 bdded2 577526; do
  PWROOT=$R uv run --project /data/personal/repos/procedural-world-generation/.claude/worktrees/agent-a859f6d1291b796bd python /tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/pw806/diag.py $w $RUNS 2>&1 | grep -v -i warn
done > $O
