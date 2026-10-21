---
id: PW-397
title: Month curves built from t_warm/t_cold put the warm month in July (north) even where compute's jul_warm says January (equatorial land of eccentric-orbit frames)
type: task
status: todo
parent: null
milestone: null
subsystem: climate
effort: s
impact: low
found_by: pw380-equator
blocked_by: []
relates: [PW-380]
refs: [planet/climate.py, planet/world.py, planet/timeline.py, planet/vegetation.py, planet/soils.py]
created: 2026-10-16
updated: 2026-10-16
---

## Description
PW-380 gave climate.compute phase-true `t_jul` / `t_jan`. compute keeps which of warmest/coldest is July
(`jul_warm`, set before its max/min), and world.seasons now uses them, so the world's
temperature_jul/jan are continuous across the equator: in finished frame bcd6c8's terrain the step went
13.5 -> 0.7 C. Two consumers still assume the warm month is July in the north:
- `climate.months` (and so vegetation.site, soils, water_balance's monthly pass, snow) builds a sine with
  its peak in July (north) / January (south) from t_warm and t_cold. Where jul_warm is the other way round,
  the warm months then fall with the wrong half-year's rain (p_jul is Apr-Sep). That happens on
  equatorial land in finished time-zoom frames with an eccentric orbit (to ~10-15 deg, swings of 13 C there)
  and by ~1 C on a few equatorial cells in plain worlds (the rainy half-year cooler).
- `timeline.py` keyframes map July/January as `where(lat >= 0, t_warm, t_cold)` (runs have no orbit_dt, so
  only the ~1 C cases).
What to try: pass months() the hemisphere-convention pair (t_sum = where(north, t_jul, t_jan), t_win the
other). A negative amplitude then gives the right phase, as long as nothing in months() assumes
t_warm >= t_cold. Or give months a phase flag. For the keyframes, keep jul_warm in the run's state
next to t_warm/t_cold.
- [ ] months()' warmest month matches t_jul/t_jan's on every cell of a finished eccentric-orbit frame

## Updates
- 2026-10-16: Created from inbox draft draft-month-curves-phase-at-equator.md (found by pw380-equator).
