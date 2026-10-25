#!/bin/bash
# Earth (577526) anchor runs, before and after: warming at today's CO2, Eocene-like warm high CO2, LGM-like cold low CO2
S=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/pw806
WT=/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-a859f6d1291b796bd
cd $WT
for R in $S/before $WT; do
  echo "== $R"
  PWROOT=$R uv run python $S/diag.py ${WORLD:-577526} 350:0 280:0 350:3 350:6 560:3 700:6 1000:6 280:-4 185:-5 155:4 2>&1 | grep -v -i warn | cut -c1-110
done
