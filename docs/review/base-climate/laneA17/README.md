# Lane A17: PW-594 (SH boundary currents), then the SH coastal summer winds

Results are in `../stages.md`, section "PW-594 and the SH coastal summer winds (lane A17)". Base: main d01c772 + lane
A16's branch (b04a5fc), merged as 1a68a7e. Step 1 is committed on the branch; step 2 and the PW-593 retry are saved
diffs only.

Scripts (run from anywhere; they find the tree from their own path, and import `planet` before numpy):
- `tools.sh SUFFIX`: earth_check, climate_bias, `p3.py` (lane A15's stage-3 probe), `wdiag.py` (A15's summer-wind
  table), `wbc.py`, and the overturning (Earth + the 9 worlds), 6 processes at once. Outputs `*_SUFFIX.txt`.
- `summ.py SUFFIX ...`: the bars side by side. `bars.md` = base / step1 / step2; `bars_pw593_on_step2.md` = step 2
  with PW-593's summer layer (`ml_wind`) and the storm-transient stirring wind (`ml_storm` 0.5 / 1).
- `wbc.py ['k=v,...']`: per box the SST's parts (t_eq, gyre anomaly, moc), sea air vs NCEP, the current, the summer
  wind; and the coastal profiles along the SH east coasts.
- `gyre.py`: the annual zonal wind and curl forcing per SH basin, which islands wall the gyres, psi in the Tasman.
- `curmap.py LAT0 LAT1 LON0 LON1 ['k=v']`: a text map of the current and the gyre anomaly.
- `patag.py`: A15's SH-coast anomaly / wind-part probe.

Diffs (apply to the branch head 7b41cea's `planet/climate.py`, which is step 1):
- `step2_stable_summer.diff`: step 2 (the land's air in summer lies stable over the sea: `_sea_half` returns the
  summer and winter halves, `chill` in `sea_surface`), relative to 7b41cea: `git apply` it on the branch head, then
  `pytest tests/test_golden.py --update-golden`.
- `pw593_on_step2_toggles.diff`: step 2 plus the `ml_wind` / `ml_storm` probe toggles (relative to 1a68a7e).

Suffixes: `base` = 1a68a7e (A16's branch, identical to A16's `*_branch.txt`), `step1` = 7b41cea, `step2` = step 1 +
`step2_stable_summer.diff`, `s2_ml*` = step 2 + the toggles.
