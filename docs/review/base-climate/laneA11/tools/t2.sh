#!/bin/bash
# usage: t2.sh tag  -> out/t_*_tag.txt: the endings test and the cold-moment sheets test (+ test_climate), and the Earth probe
cd /data/personal/repos/procedural-world-generation/.claude/worktrees/agent-abbf08ba762366c44 || exit 1
S=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/laneA11
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMBA_NUM_THREADS=6
uv run pytest -q -s -n 0 -p no:cacheprovider tests/test_timezoom_cycle.py::test_glacials_grow_ice_and_endings_melt_it_fast > $S/out/t_end_$1.txt 2>&1 &
uv run pytest -q -n 4 -p no:cacheprovider tests/test_timezoom_consistency.py tests/test_climate.py > $S/out/t_cold_$1.txt 2>&1 &
PYTHONWARNINGS=ignore uv run python $S/p3.py > $S/out/p3_$1.txt 2>&1 &
wait
grep -h "glacial extra ice (m): [0-9]\|passed\|failed\|^FAILED" $S/out/t_end_$1.txt $S/out/t_cold_$1.txt
grep -o "W Europe [^|]*" $S/out/p3_$1.txt
cut -c1-330 $S/out/p3_$1.txt
