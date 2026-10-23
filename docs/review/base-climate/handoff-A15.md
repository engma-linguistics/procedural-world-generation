# Handoff: base-climate lane A15 (PW-596 option A)

Branch `worktree-agent-a2d94046b3c8a7056`, based on main d32f7fa (before PW-576). The results are in `stages.md`,
section "PW-596 option A", and the files in `laneA15/`.

## State
- `planet/climate.py` has two changes:
  - `westerly_belt`: the westerlies by season and hemisphere, from each season's zonal-mean contrast relative to
    the planet's own mean. They enter through `wind(belt=)`.
  - `low_column`: thermal lows as deep as the land's air column. It enters through `monsoon_wind(column=)`.
  - Goldens updated on purpose.
- PW-593's summer layer (`ml_wind`) is not on the branch. It still fails on the new winds. The toggled probe code is
  `laneA15/pw596_probe_toggles.diff`: `X_BELT` / `X_COL` env toggles and `ml_wind=1/2`.
- `pytest`: 2 time-zoom ice tests are red (endings, cold-moment sheets). The health sweep's ice-age outliers are
  worse. Both are in `issue-tracking/inbox/draft-pw596-winds-break-timezoom-ice-tests.md` (needs-decision).
- The SH coasts' summer winds are still calm. That is the next step before PW-593:
  `draft-sh-coastal-summer-winds-still-calm.md`.

## When MERGE MAIN lands (PW-576)
- Merge main, re-run `pytest --update-golden`, and re-take the baselines. Main's are lane A14's `*_before.txt`,
  `laneA15/wind_before.txt` and `health_before.md`.
- Then `laneA15/tools.sh <suffix>` (earth_check, climate_bias, the overturning on Earth and the 9 worlds), `p3.py`,
  `wdiag.py`, `twotests.sh <tree>` and `tools/health.py --quick`.

## Tools
- `wdiag.py`: summer / winter wind per box, split by part.
- `patag.py`: SH-coast anomalies.
- `runp3.sh OUT "belt col [tune suffix]"`: p3 variants in parallel, for the probe diff only.
- The Earth data are a symlink: `data/earth` -> the main checkout's (gitignored).
