---
title: "test_timezoom_consistency::test_ice_at_index_zero_is_the_runs rides on a chaotic 300 Myr L5 run: PW-582 attempt 2 gives a different world (6 plates against 13, sea level -314 m against +5) and -26.0 m against the 25 m bound"
type: task
status: needs-decision
parent: null
milestone: null
subsystem: timezoom
effort: s
impact: high
found_by: base-climate-laneA8
blocked_by: []
relates: [PW-582, PW-366, PW-471]
refs: [tests/test_timezoom_consistency.py, docs/review/base-climate/stages.md]
---

## Description
`cold_moment` builds its source from `run_sim(level=5, seed=4, myr=300)`, a full run whose climate feeds back on
the tectonics and erosion. Any change to the climate gives a different world, not the same world with a different
climate. Lane A8's PW-582 attempt 2 (the inflow's salinity mixes along its way, one line in `ocean.overturning`) moves
the test's last-frame sea-level change from -21.0 m to -26.03 m (bound: 25 m).

The two worlds the fixture builds (scratchpad `laneA8/sl.py`, last frame's stats):

| | attempt 1 (ee0cc87) | attempt 2 |
|---|---|---|
| plates / largest landmass | 13 / 10.8% | 6 / 26.9% |
| sea level | +4.9 m | -314 m |
| ice / its volume | 6.6% / 51.4 Mkm3 | 5.3% / 39.3 Mkm3 |
| overturning N / S | 3.5 / 5.4 Sv | 1.7 / 1.0 Sv |
| sea-level change over 20 kyr | -21.0 m | **-26.0 m** |

So the failure says nothing about the change itself: it is another world. It is the same kind of problem as
`test_run_lakes` (ruled a harness change: search 60 steps). Handoffs A6 and A7 already noted that the time-zoom tests
react to any change in the overturning, which is this.

Every ocean or climate change in lane A (PW-582, PW-579 next) will keep landing on this. Options (all test changes,
so for the coordinator):
- A: build the fixture's source from a fixed stored state (e.g. the run's state at 300 Myr frozen into a test
  fixture file), so climate changes act on one world;
- B: a short run (less chaos) or a synthetic source with known sheets;
- C: leave it, and treat each failure as a coin toss to re-roll by hand.

- [ ] rule on A / B / C
