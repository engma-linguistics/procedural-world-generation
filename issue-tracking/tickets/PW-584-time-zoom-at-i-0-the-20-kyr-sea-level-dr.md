---
id: PW-584
title: "Time zoom at I = 0: the 20 kyr sea-level drift ranges from -0.1 to -29 m over plausible L5 worlds, so the 25 m bound of test_ice_at_index_zero_is_the_runs sits inside the spread"
type: task
status: todo
parent: PW-470
milestone: v2
subsystem: timezoom
effort: m
impact: med
found_by: base-climate-laneA9
blocked_by: []
relates: [PW-366, PW-471, PW-418]
refs: [tests/test_timezoom_consistency.py, docs/review/base-climate/stages.md]
created: 2026-10-22
updated: 2026-10-23
---

## Description
Lane A9 made `cold_moment` search seeds 4-11 for a source that meets a stated precondition: run sea level within
150 m, at least 2 Sv of overturning in each hemisphere, and at least 25% land poleward of 60 deg in one hemisphere.
This is the coordinator's ruling 1, and the assertions are unchanged. The test passes on main, on PW-582 attempt 2,
and on attempt 3.

The same measurement over seeds 4-11 (300 Myr, L5, PW-582 attempt 3; `scratchpad/laneA9/tzseed.py`) gives the last
frame's `sea_level_change_m`:

| seed | run sea level | N / S Sv | sheets | drift (m) |
|---|---|---|---|---|
| 4 | -56 | 4.8 / 10.5 | 3.0% | -23.0 |
| 5 | -31 | 17.6 / 18.5 | 1.5% | -8.0 |
| 6 | -82 | 17.9 / 0.0 | 0.4% | -0.1 |
| 7 | -49 | 13.8 / 10.6 | 1.5% | **-29.1** |
| 8 | -120 | 6.6 / 12.6 | 2.8% | -11.6 |
| 9 | +20 | 1.4 / 0.0 | 1.2% | -9.3 |
| 10 | -186 | 6.7 / 6.4 | 1.3% | -24.3 |
| 11 | -75 | 0.3 / 10.3 | 2.5% | -2.7 |

On main the spread is similar (-6 to -32 m over seeds 1-8). Seed 7 is an ordinary world, and its drift is past the
bound. The drift is always ice growth (negative sea level), so at I = 0 the zoom does not quite keep the run's ice.
That is the PW-366 / PW-471 property itself, not the harness. The test passes because the first plausible seed
happens to be under 25 m.

- [ ] find what grows ice at I = 0 on seed 7 (the zoom's balance against the run's ice rule), or rule that the bound
  is per-world and widen the test to several seeds

## Updates
- 2026-10-23: Milestone v1 -> v2 (owner approved shrinking v1 to its real gates, 2026-10-24; docs/review/board/triage-2026-10-24.md).
- 2026-10-22: Created from inbox draft draft-timezoom-index-zero-drift-spread.md (found by base-climate-laneA9).
