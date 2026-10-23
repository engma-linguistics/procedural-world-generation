# Lane A23: PW-646 option C, a real pCO2 in the run

Results are in `../stages.md`, in the section "PW-646 option C: the run carries a real pCO2 (lane A23)".

Run every script from a tree root with `PYTHONPATH=.`.

- `co2_choices.py` writes `co2_choices.txt`:
  - Earth's glacial pCO2 under each reading (reference, sensitivity);
  - C3 quantum yield against today's at low pCO2.
- `lowtail.py [level]` writes `lowtail_L6.txt`: Earth's plants grown at 350-124 ppm on dT 0 and +3. It reports NPP,
  tropical trees, the forest, savanna-grass and desert areas, and the hot-month C3 failures.
- `tz_earth_c.txt/.json` is `tools/tz_earth.py --level 6` on this branch.
- `health_c/` and `health2_c/` are `tools/health.py --quick` on this branch.
  - `health_c/` uses the default seeds.
  - `health2_c/` uses seeds 101-108. It was re-reported with `--manifest` after a pause had stopped the sweep, so it
    has no determinism re-run.
- `htable.py` writes `htable.txt`. It compares main, A22 and A22 + C on both draws:
  - main and A22 come from `../laneA22/`;
  - the ppm columns read the frames' `co2` as 350 x e^co2.
