# Lane A20: PW-592, shelf and marginal seas starved of the open ocean's heat

Results are in `../stages.md`, section "PW-592: the shelf seas take the air the wind brings (lane A20)".
Base: main 59b83d7 (PW-596's winds and PW-594's island walls). Main's Earth bars are lane A17's step-1 files
(`../laneA17/*_step1.txt`). `p3.py` and `seabox.py` reproduce them exactly on 59b83d7, and the run and climate code
are the same. Scripts import `planet` before numpy (lane A16's trap).

- `shelfdiag.py ['k=v']`: per sea box, the SST's parts (t_eq, the gyre carry, the overturning's heat, the inflow's
  share and temperature, its transport, the current, the depth) against the observed annual air.
  `shelfdiag_main.txt`, `shelfdiag_slopelat.txt` (probe: PW-582's slope current from 25 / 35 / 40 deg, dropped),
  `shelfdiag_probe1.txt` (the first, own-reach version of the shelf rule), `shelfdiag_branch.txt`.
- `eumap.py ['k=v'] [eu|asia]`: 2-degree text maps around NW Europe of sst - obs air, moc heat, share, gyre carry and
  depth (`eumap_main.txt`).
- `tools.sh SUFFIX`: earth_check, climate_bias, `../laneA17/p3.py`, `../laneA18/seabox.py`, then the overturning on
  Earth + the 9 worlds. `*_branch.txt` is the first version (annual land air, which froze Hudson Bay), `*_branch2.txt`
  the winter clipped at freezing (too warm: Okhotsk, Keewatin), and `*_branch3.txt` the committed one (`_open_air`).
- `p3_probe2.txt`, `p3_step2_probe2.txt`, `p3_step2_probe3.txt`: the probe on main and on A17's step 2, with and
  without A18's shelf-depth layer (PW-633's `shelf_probe`). `step2_shelfair_probe.diff` is that probe tree.
- `step2_on_branch.diff`: A17's step 2 plus the `shelf_probe` toggle on the branch head (1d076ad);
  `p3_step2_branch.txt`, `seabox_step2_branch.txt`.
- `xforest.py`: `test_glacial_cooling_turns_forest_to_tundra_and_cools_further` crossed (sim4 built with or without
  `_shelf_air`, then the test's numbers with or without it; `WORLD=on|off CLIMATE=on|off`).
- `pytest_branch.txt`: the tail of `pytest -q` on the branch.
- `health.sh`: `tools/health.py --quick` on main 59b83d7 (a detached worktree) and on the branch, 2 x 2 workers;
  `health_main/`, `health_branch/`.
