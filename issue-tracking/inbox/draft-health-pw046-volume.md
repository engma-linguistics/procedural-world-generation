---
title: "PW-046 update: continental crust volume falls 3-8% over 1 Gyr on all 11 sweep runs; land and crust area now on target"
type: task
status: todo
parent: null
subsystem: tectonics
effort: s
impact: low
found_by: health-sweep
blocked_by: []
relates: [PW-046, PW-238]
refs: [docs/review/health/2026-10-15/report.md, tools/health.py]
---

## Description
Update for PW-046. PW-246 health sweep (2026-10-15, main 6926583, 8 L6 + 3 L7 seeds, 1 Gyr): the
land and area part of this ticket looks settled, the volume part has turned into a slow loss.
- land: seed medians 30.8-31.5% at L6, 32.2-32.3% at L7 (Earth 29%); maxima 37.7-38.7% when assembled.
- continental crust area: medians 39.4-40.2% (L6), 38.8-39.0% (L7); ranges 35-44%.
- mean continental thickness: medians 33.9-34.9 km (L6), 34.9-35.9 km (L7); target 35 (PW-238).
- continental crust volume (sum of thickness over continental cells), end / start: L6 0.918 (seed 11),
  0.925 (77, 3199), 0.934-0.936 (42, 505, 1), 0.955 (2), 0.974 (21); L7 0.933 (3199), 0.950 (21),
  0.958 (11). Every run loses 3-8%, none gains (the ticket's mid-run +2-5% drift is gone).
Whether a slow loss is wanted is a judgement call (Earth's continental volume is thought roughly
steady or slowly growing over the last Gyr); the volume thermostat could aim at the starting volume.
If that's accepted, PW-046 can close.
