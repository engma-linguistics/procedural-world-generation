---
title: test_zoom_soil_layers' floodplain wet share follows the fixture continent's rain (0.519 on main, knife edge)
type: task
status: needs-decision
parent: null
subsystem: zoom
effort: s
impact: low
found_by: laneA4 (PW-578 attempt 2)
blocked_by: []
relates: [PW-578, PW-331]
refs: [tests/test_zoom_soils.py, planet/soils.py, tests/test_zoom_vegetation.py]
---

## Description
`test_zoom_soils::test_zoom_soil_layers` asserts that more than half of the big rivers' floodplain pixels (river_q
≥ 300, on the river, < 3 m above it) are alluvium, gley or peat. On main the share is 0.519. With stage 2b plus
PW-578 attempt 2 it is 0.488:

| | plain pixels | ALLUVIUM | GLEY | PEAT | ACRISOL | LUVISOL | CAMBISOL | other | wet share | rain on the plain |
|---|---|---|---|---|---|---|---|---|---|---|
| main | 640 | 242 | 37 | 53 | 204 | 83 | 21 | 0 | 0.519 | 1863 mm |
| attempt 2 | 594 | 207 | 27 | 56 | 191 | 88 | 21 | 4 | 0.488 | 1706 mm |

The driver: the fixture's synthetic continent (38N, 10E) gets ~8% less rain. The rivers carry less, so fewer
pixels pass river_q ≥ 300, and fewer reach `alluvial ≥ 0.6` (`soils._mineral`; the zoom's floodplain share).
Nothing in soils changed. The dry floodplain pixels are ACRISOL / LUVISOL: the floodplain's alluvium share is below
0.6 there, not the climate's soil choice.

Main itself passes by 1.9 points, so the line is about the fixture's rain, not the soils logic. Options:
- A: ask whether a floodplain pixel with `alluvial` 0.5–0.6 should be alluvium (soils' own rule).
- B: a fixture whose rivers are big by construction, independent of the climate.
- C: accept that climate changes move it, and rule it may be re-baselined.

Lean: B, since the test checks the soils, not the rain.
