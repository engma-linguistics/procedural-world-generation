---
id: PW-467
title: "Time zoom vs run: measure the zoom's time-mean ice against the run's (tool + slow test), the acceptance metric for the cycle-average framing"
type: task
status: todo
parent: PW-470
milestone: v2
subsystem: timezoom
effort: s
impact: high
found_by: pw462
blocked_by: []
relates: [PW-462, PW-436, PW-366, PW-461]
refs: [tests/test_timezoom_consistency.py, planet/timezoom/sim.py, docs/review/audit/ice-framing-deep-dive.md]
created: 2026-10-20
updated: 2026-10-23
---

## Description
PW-462's framing says a time zoom is a window on the run's cycles, so the zoom's *time-mean* ice should
match the run's ice, while its start and end needn't. Nothing measures that today: the only consistency
test (`test_unforced_start_stays_near_balance`) runs 20 kyr with no orbit, CO2 or ice albedo and checks the
start drift against 25 m. On main the stored and measured zooms all start at one *edge* of their own range
(the run's ice is the zoom's interglacial on moderately cold moments, its glacial on deep ones), with
time-mean offsets of -68 to +137 m (docs/review/audit/ice-framing-deep-dive.md, section 2).

Build the measurement first, so every later ice-age change is judged by it:
- `tools/tz_mean.py`: for a list of moments (in-memory `run_sim` moments, or stored runs' keyframes; never
  writing to the real store), run the default forced zoom for `--kyr` (default 400) and print the run's sea
  level from ice, the zoom's time-mean (all, and after the first 100 kyr), min, max, where the start sits in
  the range (percentile), the time-mean iced area against the run's, endings and backstops. Moments:
  the consistency fixture (L5 seed 1 @ 300, -4 C), L6 seed 11 @ 400, seed 2 @ 580, seed 2 @ 620, Earth.
- A slow test (`tests/test_timezoom_mean.py`) on the L5 fixture, 300 kyr (~20 s of zoom): the zoom's
  time-mean sea level after 100 kyr within max(15 m, 0.25 x the zoom's swing) of the run's, and the time-mean
  iced area within 25%. Mark it xfail(strict) until the run-side rule lands (draft-run-ice-cycle-mean.md),
  so it flips to a pass when it's honest.
- Keep the unforced 20 kyr test as the *rule* consistency check (shared mass balance and profile); the new
  test replaces it as the *framing* check. When the run's rule becomes a mean of orbital states, the unforced
  test moves to "the zoom held at one orbital state, from the run's equilibrium for that state, drifts < 25 m
  in 20 kyr" (both the warmest and the coldest state).
- [ ] tool prints the table for the 5 moments; numbers go in the deep-dive doc
- [ ] slow test in place (xfail strict on main)

## Updates
- 2026-10-23: Milestone v1 -> v2 (owner approved shrinking v1 to its real gates, 2026-10-24; docs/review/board/triage-2026-10-24.md).
- 2026-10-20: Created from inbox draft draft-tz-mean-matches-run-check.md (found by pw462).
