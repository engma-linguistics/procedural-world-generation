#!/bin/bash
# usage: checks.sh <step tag>  -- full suite + health defaults, then the two draws + health 101-108, in this worktree
W=/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-afb6b6cb29caddd7f
S=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/m1024
t=$1
cd $W
( start=$(date +%s); uv run pytest -q > $S/$t.full.txt 2>&1; echo "exit $? wall $(( $(date +%s)-start )) s" >> $S/$t.full.txt ) &
uv run python tools/health.py --quick --workers 8 --out $S/h_${t}_def > $S/h_${t}_def.log 2>&1 &
wait
( OFFS="0.001 -0.001" W=6 bash $S/draws.sh $t tests/test_timezoom.py tests/test_timezoom_cycle.py tests/test_timezoom_consistency.py ) &
uv run python tools/health.py --quick --l6 101 102 103 104 105 106 107 108 --workers 8 --out $S/h_${t}_101 > $S/h_${t}_101.log 2>&1 &
wait
$S/main_tree/.venv/bin/python $S/hsum.py main_def=$S/h_main_def/report.md ${t}_def=$S/h_${t}_def/report.md main_101=$S/h_main_101/report.md ${t}_101=$S/h_${t}_101/report.md
tail -2 $S/$t.full.txt
for f in $S/$t.off*.txt; do echo "== $f"; grep -E "with sheets|eligible seeds pass \(|passed|failed|^exit" $f; done
