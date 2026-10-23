# Lane A18: PW-627's step 2 crossed, the endings test, and Europe's summer layer

Results are in `../stages.md`, section "PW-627 step 2: the endings test crossed, and Europe's summer layer (lane A18)".
Base: main b900f1c + lane A17's branch (3e9855a, A16's winds + PW-594's island walls), merged as 644a4f0. Since
3e9855a main changed no run or climate code (game attributes, export), so A17's step-1 / step-2 bars stand on this
tree (`seabox`/`p3` reproduce them exactly). Step 2 is not committed (see stages.md); it is
`../laneA17/step2_stable_summer.diff`, applied on 644a4f0.

The scripts import `planet` before numpy (lane A16's trap). The step-1 tree is a detached worktree at 644a4f0 in the
session scratch (`$S1WT`, default `<scratch>/a18_step1`, with `data/earth` symlinked).
- `xzoom.py` / `xzoom.sh`: lane A16's crossing of `test_glacials_grow_ice_and_endings_melt_it_fast`. `xzoom.sh dump`
  pickles sim4's source (L4, seed 1, 300 Myr) from each tree; `xzoom.sh zoom "TREE SRC" ...` runs the test's numbers
  on SRC's world with TREE's climate. `xzoom_cross.txt` is the 2 x 2.
- `seedscan.sh SEED...`: the same numbers on the L4 300 Myr run of other seeds, each tree with its own climate
  (`seedscan_2-9.txt`).
- `xflows.py SRC.pkl`: the zoom's ice budget (accumulation, ablation, calving) around the first ending.
- `depth.py`: Earth L6 sea depths in the near-land boxes.
- `seabox.py ['k=v']`: per sea box, the SST's parts and step 2's summer / winter halves, chill, land_air
  (`seabox_step1.txt`, `seabox_step2.txt`; `WT=` for another tree).
- `step2_shelf_probe.diff`: step 2 plus the probe toggle `shelf_probe` (the seasons' layer no deeper than the sea
  floor), relative to 644a4f0.
- `pytest_step2.txt`: the tail of `pytest -q` on step 2 (goldens regenerated, not committed).
