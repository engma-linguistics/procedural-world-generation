# Merge lane 2026-10-24 (serial run-physics lane)

Branch `worktree-agent-afb6b6cb29caddd7f`, from main 52f25a9. Each step is its own commit, measured before the next.
Draws are `PW_SEED_OFFSET` (climate_offset 0, +0.001, -0.001 C). Health is `tools/health.py --quick --workers 8`
(L6, 500 Myr) on two seed sets (defaults 1 2 11 21 3199 42 77 505; 101-108), main's own tree (an export of 52f25a9)
run in the same session. `hsum.py` pools a sweep's report.md: the % of keyframes with ice sea level below -150 m
(mean over seeds; every seed has the same keyframes), seeds above 10%, old / new ice-bar fails, icehouse %.

## Main 52f25a9 (baseline)

| sweep | pooled % kf < -150 m | seeds > 10% | old bar F | new bar F | icehouse % median / mean |
|---|---|---|---|---|---|
| defaults | 4.2 | 2 (2, 42) | 0 | 4 | 17.6 / 28.7 |
| 101-108 | 3.4 | 1 (103) | 0 | 2 | 27.4 / 30.6 |

(`main/health_def.md`, `main/health_101.md`. A23 measured 3.8% on the defaults.)

## Step 1: PW-660, L5 cold-moment window 25-50 -> 25-75

Harness only: `SEEDS` in tests/test_timezoom_consistency.py. MIN_SHEETED, `_plausible` and every assertion unchanged.

| draw | sheeted of plausible (need 5) | speeds | index stays zero | ice at index zero | result |
|---|---|---|---|---|---|
| 0 | 13 of 27 | 13 / 13 (bar 10) | 27 / 27 | 13 / 13 (bar 10) | 3 passed, 778 s |
| +0.001 | 15 of 24 | 14 / 15 (bar 11) | 24 / 24 | 13 / 15 (bar 11) | 3 passed, 783 s |
| -0.001 | 12 of 22 | 12 / 12 (bar 9) | 22 / 22 | 11 / 12 (bar 9) | 3 passed, 776 s |

On 25-50 main gave 7 / 10 / 5. The module took ~13 min wall per draw with the three draws side by side
(`PW_SEED_WORKERS=6`, `-n 2`). Full `pytest -q`: 603 passed in 541 s, with a health sweep running alongside (the
earlier 268 s was measured with the 25-50 window on a less loaded machine); the module is the suite's long pole.

## Step 2: merge A22 + A23 (PW-644, PW-646 C), head 83b2036

Clean merge (no conflicts, goldens as the branch had them). Full `pytest -q`: 603 passed in 589 s. The three
time-zoom modules on the re-rolled draws:

| draw | forest (bar) | endings (bar 12) | sheeted (need 5) | speeds | index zero | ice at index zero | result |
|---|---|---|---|---|---|---|---|
| +0.001 | 14 / 18 (9) | 18 / 24 | 12 of 26 | 12 / 12 | 26 / 26 | 11 / 12 (9) | 38 passed |
| -0.001 | 17 / 18 (9) | 17 / 24 | 14 of 24 | 14 / 14 | 24 / 24 | 13 / 14 (10) | 38 passed |

Health (same session as main's):

| sweep | pooled % kf < -150 m | seeds > 10% | old bar F | new bar F | icehouse % median / mean |
|---|---|---|---|---|---|
| defaults | 4.2 -> 8.6 | 2 -> 2 (1, 77) | 0 -> 0 | 4 -> 3 | 17.6 / 28.7 -> 22.6 / 34.3 |
| 101-108 | 3.4 -> 3.2 | 1 -> 1 (105) | 0 -> 0 | 2 -> 3 | 27.4 / 30.6 -> 34.3 / 41.2 |

A23's "3.8% main vs 5.9%" is the mean over both sets: (4.2 + 3.4) / 2 = 3.8 and (8.6 + 3.2) / 2 = 5.9. Confirmed
exactly: the merged tree's sweeps are identical, seed for seed, to A23's `health_c` and `health2_c`. Old ice-bar
fails: 0. Earth L6 (dT 0) is unchanged by the merge (`main/earth`, `step2/earth`): rain log-r 0.630, W Europe
warmest 17.1 vs 18.0 (-0.9), SH coastal range 12.5, North Sea annual SST 6.9, NH sinking 13.86 Sv (90% open polar),
Norwegian coast open in winter 100%.

## Step 3: merge A20 shelf air (PW-592), head a1462d3

Conflicts: `docs/review/base-climate/stages.md` (both sides appended a section: kept both) and
`tests/golden/sim_L4_s1_60myr.json` (regenerated on purpose with `--update-golden`: A20's and A23's output changes
together; `climate_L4.json` as A20 had it, which the regeneration reproduced unchanged). Full `pytest -q`: 603
passed in 570 s.

| draw | forest (bar) | endings (bar 12) | sheeted (need 5) | speeds | index zero | ice at index zero | result |
|---|---|---|---|---|---|---|---|
| +0.001 | 16 / 22 (11) | 21 / 24 | 18 of 25 | 18 / 18 | 25 / 25 | 16 / 18 (13) | 38 passed |
| -0.001 | 15 / 22 (11) | 22 / 24 | 15 of 24 | 15 / 15 | 24 / 24 | 13 / 15 (11) | 38 passed |

Health (main -> step 2 -> step 3):

| sweep | pooled % kf < -150 m | seeds > 10% | old bar F | new bar F | icehouse % median / mean |
|---|---|---|---|---|---|
| defaults | 4.2 -> 8.6 -> 7.6 | 2 -> 2 -> 2 (21, 505) | 0 -> 0 -> 1 (seed 11) | 4 -> 3 -> 1 | 17.6 / 28.7 -> 22.6 / 34.3 -> 30.4 / 32.4 |
| 101-108 | 3.4 -> 3.2 -> 7.3 | 1 -> 1 -> 2 (103, 107) | 0 -> 0 -> 1 (seed 107, icehouse 100%) | 2 -> 3 -> 5 | 27.4 / 30.6 -> 34.3 / 41.2 -> 42.1 / 39.2 |

Mean over the two sets: 3.8 (main), 5.9 (step 2), 7.45 (step 3). These are single chaotic 500 Myr runs, and which
seeds go deep moves at every step (main 2, 42, 103; step 2 1, 77, 105; step 3 21, 505, 103, 107). The old ice bar
fails on 2 of 16 after A20 (0 before). Recorded, not a stop: the tests and Earth bars are green (draft
`draft-health-drift-after-shelf-air.md`).

Earth L6 (`step3/earth`): North Sea annual SST 6.9 -> 8.5, W Europe warmest 17.1 -> 17.6 vs 18.0 (-0.9 -> -0.4), so
C left A20's gains as A20 measured them. Rain log-r 0.630, SH coastal range 12.5 (<= 12.5). The overturning on Earth
is unchanged: NH sinking 13.86 Sv (8-20), 90% in open polar seas (>= 70%), Norwegian coast open in winter 100%.

## Step 4: PW-627, stable summer air off land (commit 555883d)

A17's `step2_stable_summer.diff` does not apply on the shelf-air tree (context in `compute`). A20's
`laneA20/step2_on_branch.diff` applies cleanly but also carries a default-off PW-633 probe (`shelf_probe` in TUNE,
a `depth` argument to `_sea_half`). It was applied without the probe, so the change lines are A17's exactly (checked
line for line). Goldens regenerated on purpose (`climate_L4.json`, `sim_L4_s1_60myr.json`). Full `pytest -q`: 603
passed in 632 s.

| draw | forest (bar) | endings (bar 12) | sheeted (need 5) | speeds | index zero | ice at index zero | result |
|---|---|---|---|---|---|---|---|
| +0.001 | 19 / 20 (10) | 21 / 24 | 20 of 26 | 20 / 20 | 26 / 26 | 17 / 20 (14) | 38 passed |
| -0.001 | 18 / 20 (10) | 21 / 24 | 20 of 29 | 20 / 20 | 29 / 29 | 18 / 20 (14) | 38 passed |

Earth L6 (`step4/earth`): rain log-r 0.630 -> **0.649** (>= 0.617; A17 had 0.649), SH coastal range 12.5 -> **12.2**
(<= 12.5), W Europe warmest 17.6 -> 16.6 vs 18.0 (**-0.4 -> -1.4**; A20 measured -1.6), North Sea annual SST 8.5 -> 7.9
(warmest month 15.5 -> 11.6 vs 16.4). Overturning: NH sinking 13.64 Sv, 89% in open polar seas, Norwegian coast open
in winter 100%.

Health:

| sweep | pooled % kf < -150 m (main / s2 / s3 / s4) | seeds > 10% (s4) | old bar F (s4) | new bar F (s4) | icehouse % median / mean (s4) |
|---|---|---|---|---|---|
| defaults | 4.2 / 8.6 / 7.6 / 4.4 | 1 (42) | 1 (11) | 2 | 35.3 / 33.3 |
| 101-108 | 3.4 / 3.2 / 7.3 / **20.1** | 5 (101, 103, 106, 107, 108) | 2 (101, 103) | 3 (106, 107, 108: icehouse > 70%) | 56.9 / 53.2 |

Mean over both sets: 3.8 / 5.9 / 7.45 / **12.25**. On 101-108 step 4 gives clearly deeper icehouses (5 of 8 seeds
deep, median icehouse 57%). The tests are green, the Earth bars hold, and the mechanism is physical, so step 4 stays
by the owner's principle. The icehouse depth belongs to the thermostat (PW-611 / PW-653). Recorded on PW-627 and
PW-653.

## Step 5: PW-636 earlier flora (FLORA_PACE 0.8), head adddbae (a3128cc + a draft move): NOT KEPT

Merged as 0646532 (conflicts: PW-636's Updates, both entries kept; the golden regenerated), measured, then the
branch was reset to step 4 (641ce4f). Results in `step5_not_kept/`.

**Tests: red.** Full `pytest -q`: 1 failed, 602 passed (672 s). `tests/test_timezoom.py::test_bed_settles_under_the_ice`
fails at `median |bed - want| = 47.1 m < tol 46.2 m`. It is a single-world test (sim4, L4 seed 1, made 8 C colder),
so it fails the same way on the +0.001 and -0.001 runs (the offset only re-rolls the multi-seed fixtures). Every
multi-seed test is green:

| draw | forest (bar) | endings (bar 12) | sheeted (need 5) | speeds | index zero | ice at index zero |
|---|---|---|---|---|---|---|
| +0.001 | 18 / 21 (11) | 21 / 24 | 15 of 19 | 13 / 15 (11) | 19 / 19 | 14 / 15 (11) |
| -0.001 | 19 / 19 (10) | 22 / 24 | 9 of 17 | 9 / 9 (7) | 17 / 17 | 8 / 9 (7) |

Health (step 4 -> step 5):

| sweep | pooled % kf < -150 m | seeds > 10% | old bar F | new bar F | icehouse % median / mean |
|---|---|---|---|---|---|
| defaults | 4.4 -> **17.4** | 1 -> 3 (11, 42, 77 at 88%) | 1 -> 0 | 2 -> 5 | 35.3 / 33.3 -> 53.0 / 46.1 |
| 101-108 | 20.1 -> 6.6 | 5 -> 1 (103) | 2 -> 1 | 3 -> 4 | 56.9 / 53.2 -> 42.2 / 43.4 |

Pooled over the two sets the deep share is flat (12.25 -> 12.0%) and old-bar fails fall (3 -> 1). The defaults run
much deeper and 101-108 shallower, so this is not a clear deepening over the two sets. The health stop rule
therefore does not fire, but the red test does. Earth L6 is unchanged by step 5 (`step5_not_kept/earth`).

The failure is a single chaotic world's margin (47.1 against 46.2), the class PW-623/638/640 moved to multi-seed
fixtures. Converting this test is a harness change that needs a decision, and loosening its tolerance is not
allowed: draft `draft-bed-settles-single-world.md`. PW-636 waits until that is settled.

## Summary

| step | tests (single run) | draws +0.001 / -0.001 | health pooled % kf < -150 m (defaults / 101-108; old bar F) | Earth bars |
|---|---|---|---|---|
| main 52f25a9 | - | - | 4.2 / 3.4; 0 | log-r 0.630, SH coastal 12.5, W Eur warmest -0.9, N Sea SST 6.9, NH 13.86 Sv 90% open, Norway open |
| 1 PW-660 window 25-75 | 603 passed | sheeted 15 / 12 (draw 0: 13); all green | (harness only) | - |
| 2 A22 + A23 | 603 passed | green / green | 8.6 / 3.2; 0 (A23's 3.8 -> 5.9 confirmed) | unchanged |
| 3 A20 shelf air | 603 passed | green / green | 7.6 / 7.3; 2 | N Sea 8.5, W Eur -0.4; rest unchanged |
| 4 PW-627 | 603 passed | green / green | 4.4 / 20.1; 3 | log-r 0.649, SH 12.2, W Eur -1.4, N Sea 7.9, NH 13.64 Sv 89%, Norway open |
| 5 PW-636 (not kept) | 1 failed (bed settles, sim4) | 1 failed each (same test) | 17.4 / 6.6; 1 | unchanged from 4 |

The last green step is 4: branch head 641ce4f plus this write-up.
