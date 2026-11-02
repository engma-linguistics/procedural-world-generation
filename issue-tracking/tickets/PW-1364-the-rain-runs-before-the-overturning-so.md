---
id: PW-1364
title: "The rain runs before the overturning, so it sees the N Atlantic 3-6 C too cold: the storm tracks' winter evaporation is a third of NCEP's"
type: task
status: todo
parent: PW-015
milestone: v2
subsystem: climate
effort: m
impact: med
found_by: lane132
blocked_by: []
relates: [PW-1321, PW-593]
refs: [docs/review/base-climate/rain-supply/round1.md, docs/review/base-climate/rain-supply/seaair.py, docs/review/base-climate/rain-supply/seaair_L6.txt, docs/review/base-climate/rain-supply/sstswap.py, docs/review/base-climate/rain-supply/screens.md, "planet/climate.py::compute", "planet/climate.py::_season_inputs", "planet/ocean.py::solve", tools/moisture_regions.py, docs/review/base-climate/rain-supply/round2.md, docs/review/base-climate/rain-supply/ec2.sh, docs/review/base-climate/rain-supply/summ2.py]
created: 2026-11-02
updated: 2026-11-02
---

## Description
In plain words: the model works out the rain before the deep ocean's warm inflow (the overturning). So the rain sees
the North Atlantic far colder than the finished climate has it.

Winter half, Earth L6, the N Atlantic storm track (40-60 N):

| | C |
|---|---|
| the rain's SST | 6.7 |
| the rain's sea air | 4.7 |
| the finished sea air, after the overturning | 13.1 |
| NCEP 2 m air | 8.0 |

Its winter evaporation is 452 mm against NCEP's 1339.

Screen (lane 132, sstswap.py: NCEP's sea air + 0.5 C, in the rain only):
- the N Atlantic's winter evaporation goes 452 -> 1130-1292 mm;
- its rain goes 1206 -> 1799-1925 mm (GPCP 1651).

This puts numbers on the long-noted "rain doesn't see the overturning" (PW-015, morning decision 3b). The finished N
Atlantic winter is itself 5 C warmer than NCEP. So handing the finished SST to the rain overshoots unless that is
fixed too.

What I'd try:
- a second rain pass after `ocean.solve`, warm-started from the first (RAIN_WARM_DAYS, cheap); or
- passing the overturning's share from the previous update (runs keep it in `moc_state`) into `sea_surface` before
  the rain.

Check the run cost and the PW-387 warm start.

- [ ] N Atlantic winter evaporation toward NCEP on Earth (>= 0.7x), with the humid coasts' and the interiors' rain
  ratios no worse

## Updates
- 2026-11-02: Lane 134: a second, warm-started rain pass on the overturning's sea (c680e951). Earth L7: B 24.5 -> 25.4, log-rain r 0.714 -> 0.713,
  interiors 1.85 -> 1.70x, humid coasts 0.56 -> 0.54x; N Atl winter E 452 -> 1990 (NCEP 1339): overshoots, because the finished
  N Atlantic is too warm (draft-n-atlantic-finished-sea-too-warm-for-the-rain). L6 seeds and judge: round2.md.
- 2026-11-02: Created from inbox draft draft-rain-misses-overturning-sea-warmth.md (found by lane132).
