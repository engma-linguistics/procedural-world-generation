#!/bin/bash
# Each deliberate break on wt_main (main 86d3806 + the multi-seed tests), its tests, then reverted from a backup.
S=/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/ms
BR=/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-acfa88d756b0677df
cd $S/wt_main || exit
cp $BR/tests/seeds.py $BR/tests/conftest.py $BR/tests/test_timezoom.py $BR/tests/test_timezoom_cycle.py \
   $BR/tests/test_timezoom_consistency.py tests/
run() { uv run pytest -q -n 2 -p no:cacheprovider -rA "$@" 2>&1 | grep -v "Warning\|^  fw\|^$"; }
brk() { cp "$1" "$S/bak"; }
fix() { cp "$S/bak" "$1"; }
# 1: the glacial index never ends (it stays at its maximum once an ending starts)
f=planet/timezoom/cycle.py; brk $f
sed -i 's|                x = max(x - step / p.end_kyr, 0.0)|                x = x  # BREAK: no ending|' $f
diff $S/bak $f > $S/break1.txt; run tests/test_timezoom_cycle.py::test_glacials_grow_ice_and_endings_melt_it_fast >> $S/break1.txt
fix $f
# 2: the forest loss's global term with the wrong sign
f=planet/timezoom/plants.py; brk $f
sed -i 's|dF = np.where(open_ \& self.land0, -self.p.veg_toa|dF = np.where(open_ \& self.land0, +self.p.veg_toa|' $f
diff $S/bak $f > $S/break2.txt; run tests/test_timezoom.py::test_glacial_cooling_turns_forest_to_tundra_and_cools_further >> $S/break2.txt
fix $f
# 3: the run's ice rule (earth.ice_sheets, also the cold-moment fixture's) grows no ice
f=planet/tectonics/earth.py; brk $f
python3 "$S/break3.py" $f
diff $S/bak $f > $S/break3.txt; run tests/test_timezoom_consistency.py >> $S/break3.txt
fix $f
echo done
