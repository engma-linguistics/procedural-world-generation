# Handoff: applying the PW-643 / PW-645 rulings (test-infrastructure lane)

Branch: `worktree-agent-ad946bcdcf3b84ccf`. It is main 9b30887 plus the proposal branch (merge 3ab29a1) plus commit
d62890d, the rulings in `tests/`.

## Done (d62890d)
- `tests/seeds.py`:
  - `PASS_RATE_L4 = 0.5` for the L4 tests. `PASS_RATE = 0.7` stays for the L5 drift tests.
  - `Ineligible`: a seed that raises it is listed as n/a and not counted.
  - `PW_SEED_OFFSET`: re-rolls every multi-seed run with `climate_offset` C. It is 0 in the suite.
- Forest test (`tests/test_timezoom.py`):
  - eligible when `_boreal_snow >= SEASON = 3/12`: the start's forest poleward of 40 deg lies under snow at least a
    season of the year, as a tree-weighted mean of the start's `climate.snow_cover`;
  - the check sits after the start step and before any assertion, so it never reads F;
  - bar 50%.
- Endings test: bar 50%.
- `test_ice_at_index_zero_is_the_runs`:
  - the index-is-zero assertion holds at rate 1.0 on every plausible seed. The index comes from the orbit alone, so
    a failure there is a real break, not a lottery;
  - the sea-level drift is checked at 70% on the sheeted seeds.
- `MIN_SHEETED = 5` is unchanged.
- Measurements: eligibility on 120 L4 worlds is in `eligibility.txt` and `eligibility/*.json`. Two inbox drafts.

## Measured so far (three modules, `rt.sh` in the session scratchpad)
| tree, draw | forest (eligible) | endings | sheeted (need 5) | speeds | index 0 | drift |
|---|---|---|---|---|---|---|
| main, 0 | 19/21 (bar 11) | 18/24 | 7 of 14 | 7/7 | 14/14 | 7/7 |
| main, +0.001 | 13/18 (bar 9) | 19/24 | 10 of 13 | 10/10 | 13/13 | 9/10 |
| main, -0.001 | 14/18 (bar 9) | 19/24 | 5 of 10 | 5/5 | 10/10 | 5/5 |
| A20 (main + 59b83d7..a1462d3 planet diff), 0 | 11/17 (bar 9) | 20/24 | **4 of 8, red** | 3/4 | 8/8 | 3/4 |

Main is green on all three draws. On the -0.001 draw the sheeted count sits exactly at `MIN_SHEETED`.

## Queued when PAUSE came (SIGSTOPped by the coordinator)
- `held.sh`: a20 +0.001, a22 0 / +0.001, step2 0 / +0.001. The outputs go to `scratchpad/out/*.txt`.
- `tail.sh`: `breaks.sh` on the `trees/brk` export (output in `scratchpad/brkout/`), then the full `pytest -q`
  alone, timed (`out/full.txt`).
- The trees are `git archive` exports in `scratchpad/trees/`:
  - `a20`: main + `git diff 59b83d7 a1462d3 -- planet`;
  - `a22`: main + `git diff 89cc49c 2bc750b -- planet`, which drops the harness cherry-pick;
  - `step2`: main + laneA17's `step2_stable_summer.diff`.

## Left
- Fill `@@ADOPTED@@` in `multiseed-fixtures.md` with the rules, the tables, the demos and the suite time.
- Add Updates to PW-643 and PW-645 (no status change).
- Maybe draft: MIN_SHEETED = 5 at main's low tail (5 on the -0.001 draw).
- Commit, then remove `data`/`grids` symlinks? They are untracked, so keep them.
