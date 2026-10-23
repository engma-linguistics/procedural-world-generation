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
