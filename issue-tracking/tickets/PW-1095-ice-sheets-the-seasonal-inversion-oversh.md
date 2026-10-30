---
id: PW-1095
title: "Ice sheets: the seasonal inversion overshoots the interiors' summers (Antarctic plateau, Vostok)"
type: task
status: todo
parent: null
milestone: v1
subsystem: climate
effort: s
impact: med
found_by: lane28
blocked_by: []
relates: [PW-1050, PW-336]
refs: [planet/timezoom/kernels.py, planet/icemass.py, tools/earth_check.py]
created: 2026-10-30
updated: 2026-10-30
---

## Description
In plain words. PW-1050's fix (b) made the cold air layer over thick ice (the inversion,
ICE_COOL) follow the seasons with the same yearly average: none at midsummer and twice
as strong at midwinter. The reasoning was that a sheet's margin melts in summer and is
held at 0 C. That helped Greenland's summer, but it overshoots on the high interiors,
which never melt.

earth_check, main with PW-1050 against 3a58e00d before it, on the same Earth data (C;
observed in brackets):

| | L6 before | L6 after | L7 before | L7 after |
|---|---|---|---|---|
| Antarctica warmest month (-16.1) | -15.6 | -12.1 | -15.1 | -11.7 |
| Vostok warmest month (-22.7) | -23.6 | -20.7 | -23.4 | -20.5 |
| Antarctica coldest month (-48.7) | -49.0 | -50.9 | -48.9 | -50.8 |
| Greenland coldest month (-33.0) | -46.7 | -48.5 | -46.7 | -48.4 |
| Greenland warmest month (-5.0) | -12.3 | -9.8 | -11.8 | -9.4 |
| land seasonal range 60-70 / 70-80 / 80-90 S (23 / 32 / 34) | 31 / 33 / 34 | 36 / 38 / 40 | 31 / 33 / 35 | 36 / 39 / 40 |

Annual means hardly move (+0.2 to +0.5 C). Greenland's summer error shrinks from -7.3 C to
-4.8 C (L6). But Antarctica's summer is now 4 C too warm, Vostok's 2 C too warm, the
Antarctic seasonal range is 5-13 C wider than observed (it was 1-8 C too wide), and
Greenland's coldest month is 2 C further off.

A physical lead (coordinator, 10-30): an interior plateau never melts, and it keeps a
strong inversion even in summer. On the Antarctic plateau the summer sun is weak, and the
snow still radiates heavily. So the seasonal swing from (b) probably belongs on melting
or margin ice, with interiors closer to a year-round inversion. For example, the
amplitude could scale with the cell's summer warmth, or with how close it is to melting.

A follow-up to PW-1050, not a revert: (b) fixed the margins' summer double count, which
the run's ice balance depends on. Any change here needs the run's judge as well as
earth_check, since margin summers set the sheets' extent.

- [ ] The inversion's seasonal amplitude made to depend on whether the ice melts (margin vs interior), still one rule shared by the run, worlds, zoom and time zoom
- [ ] earth_check: Antarctic and Vostok warmest month and the south polar seasonal range back near observed, with Greenland's summer no worse than after PW-1050
- [ ] Run judge: passes and ice paths not worse than PW-1050's (14/18 at L6, roll 0.0005)

## Updates
- 2026-10-30: Lane 57. The inversion's swing is now scaled by the share of the warmest month's days the arriving air is above 0 C (the degree-day spread). The annual mean is unchanged, and there is no new constant (timezoom.kernels.climate_step; the zoom's inverse alternates its bisections). earth_check L6, main vs this: Antarctica warmest month -12.3 vs -14.0 (obs -16.1), coldest -50.9 vs -49.2 (-48.7); Vostok warmest -20.8 vs -22.8 (-22.7); south polar land range 36/38/40 vs 33/35/36 (23/32/34). Greenland warmest -9.8 vs -11.4 (-5.0), coldest -48.5 vs -46.9 (-33.0): it keeps ~0.9 of (b)'s 2.5 C summer gain, because its inland ice never melts and is too cold all year (inbox draft). Judge, 18 L6 draws at roll 0.0005, main vs this: passes 13 vs 14, iceboxes 8 vs 7, end T median -0.2 vs +1.3 C (paired +0.7, CI -4.4..+4.7), arid 21.9 vs 22.3%, deep-ice share median 0.19 vs 0.12. Write-up: docs/review/base-climate/ice-loop/README.md.
- 2026-10-30: Created from inbox draft draft-sheet-interior-inversion-seasonality.md (found by lane28).
