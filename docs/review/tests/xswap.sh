#!/bin/bash
S=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/ms
BR=/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-acfa88d756b0677df
declare -A T=([main]=$BR [s2]=$S/wt_s2 [a20]=$S/wt_a20)
for t in main s2 a20; do (cd ${T[$t]} && PYTHONPATH=.:tests uv run python $S/xswap.py dump $S/src4_$t.pkl 2>/dev/null); done
for c in main s2 a20; do for w in main s2 a20; do
  echo "climate $c on world $w: $(cd ${T[$c]} && PYTHONPATH=.:tests uv run python $S/xswap.py run $S/src4_$w.pkl 2>/dev/null | tr '\n' ' ')"
done; done > $S/xswap.txt
echo done
