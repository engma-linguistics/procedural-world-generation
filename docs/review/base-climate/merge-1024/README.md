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
