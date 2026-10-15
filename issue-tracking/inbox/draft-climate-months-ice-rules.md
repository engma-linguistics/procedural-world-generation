---
title: Ice and glacier snow rules stay on their own analytic year (PW-200 remainder)
type: task
status: needs-decision
parent: null
subsystem: climate
effort: s
impact: low
found_by: vegclim
blocked_by: []
relates: [PW-200]
refs: [planet/tectonics/earth.py, planet/zoom.py, planet/timezoom.py, planet/climate.py]
---

## Description
PW-200 moved `climate.koppen` onto the twelve months (`month_temps`, `month_rain`, as `climate.months`; Earth Koppen agreement 38.9 -> 38.8% exact, 71.9% group either way). The other three callers were left alone (vegclim branch), because switching them is either output-neutral or not sane, and their files were owned by other agents that night (ice: earth.py and timezoom.py; vegzoom: zoom.py):
- `earth.degree_days` (run ice sheets): the same sine year as `month_temps`; the annual positive-degree-day sum doesn't depend on which month peaks, so the only difference is the day spread (sd 5 C here, 4 C in `months`' GDD5). Switching = sharing one helper, outputs ~unchanged.
- `zoom` glacier snow (`precip x share of the year below 0 C`) mirrors `earth.ice_sheets`' rule on purpose: zoom glaciers must agree with the run's ice. Switch only together with the run's rule.
- `timezoom` monthly snow runs inside the orbital kernel with per-month insolation anomalies, which `climate.months` doesn't model; switching would mean adding orbital forcing to `months`.

Options: A) leave as is and close PW-200 (lean: the rules are consistent with each other and nearly equivalent); B) one shared degree-day helper in climate used by earth.py and zoom.py (cosmetic, golden update); C) give `climate.months` an optional insolation anomaly so the time zoom can use it too (bigger, only worth it with other time-zoom work).
