---
id: PW-456
title: "Time zoom: the cycle's summer-sun metric (months 3-4 raw) is half a month after the mass balance's warm month (2-3); corr 0.57"
type: task
status: todo
parent: PW-470
subsystem: timezoom
effort: s
impact: low
found_by: pw033
blocked_by: []
relates: [PW-440, PW-448]
refs: [planet/timezoom/cycle.py, planet/timezoom/events.py, planet/timezoom/sim.py]
created: 2026-10-20
updated: 2026-10-20
---

## Description
`cycle.summer_sun` (and `events.cycling_ice_sun`, the frames' `insol_65n_jul_anom`) average the raw
insolation of months 3-4 (Jun 21 - Aug 21). The kernel's warmest month (`climate_melt`, peak month 3) feels
the lagged sun of months 2-3 (May 21 - Jul 21, centred on the solstice). Over Earth's 600 kyr series the
two 65 N metrics correlate at only 0.57. Their minima are different orbits: t=592 (perihelion 356 deg, May-Jun
+28 / +10 W/m2, the warm month -6.5) against t=309.5 (perihelion 254 deg, the warm month -43.9). PW-448's
probe used the first and concluded the warmest month is *warmer* at a "glacial" orbit, and that Keewatin
needs dTg ~-9 C. At the kernel's coldest orbit it nucleates at ~-3 C (docs/review/audit/PW-033-diagnosis.md
section 2). The cycle's building and ending decisions key on the late metric.
What to try: use the same lagged warm-month (or melt-season PDD-weighted) sun in cycle.py, events.py and
the frames. Re-check the cycle's endings and backstops on Earth.
- [ ] one summer-sun metric shared by the kernel and the cycle

## Updates
- 2026-10-20: Created from inbox draft draft-cycle-summer-sun-month-offset.md (found by pw033).
