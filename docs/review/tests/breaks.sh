#!/bin/bash
# Each deliberate break on an export of this branch (main + the adopted multi-seed tests), its test, then reverted
# from a backup. usage: breaks.sh TREE OUTDIR (TREE: a `git archive` export of the branch with data/ and grids/ linked)
T=$1; O=$2
H=$(cd "$(dirname "$0")" && pwd)
cd "$T" || exit
run() { PW_SEED_WORKERS=4 uv run pytest -q -n 2 -p no:cacheprovider -rA "$@" 2>&1 | grep -v "Warning\|^  fw\|^$"; }
brk() { cp "$1" "$O/bak"; }
fix() { cp "$O/bak" "$1"; }
# 1: the glacial index never ends (it stays at its maximum once an ending starts)
f=planet/timezoom/cycle.py; brk $f
sed -i 's|                x = max(x - step / p.end_kyr, 0.0)|                x = x  # BREAK: no ending|' $f
diff $O/bak $f > $O/break1.txt; run tests/test_timezoom_cycle.py::test_glacials_grow_ice_and_endings_melt_it_fast >> $O/break1.txt
fix $f
# 2: the forest loss's global term with the wrong sign
f=planet/timezoom/plants.py; brk $f
sed -i 's|dF = np.where(open_ \& self.land0, -self.p.veg_toa|dF = np.where(open_ \& self.land0, +self.p.veg_toa|' $f
diff $O/bak $f > $O/break2.txt; run tests/test_timezoom.py::test_glacial_cooling_turns_forest_to_tundra_and_cools_further >> $O/break2.txt
fix $f
# 3: the run's ice rule (earth.ice_sheets, also the cold-moment fixture's) grows no ice
f=planet/tectonics/earth.py; brk $f
python3 "$H/break3.py" $f
diff $O/bak $f > $O/break3.txt; run tests/test_timezoom_consistency.py >> $O/break3.txt
fix $f
echo done
