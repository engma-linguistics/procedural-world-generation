---
title: Huge lake's shore shelf is a dead-flat land plain (4700 km2 at 1718-1747 m in the Costa Rica zoom)
type: task
status: todo
parent: null
milestone: null
subsystem: zoom
effort: m
impact: med
found_by: pw522
blocked_by: []
relates: [PW-521]
refs: [planet/zoom.py, "zoom 32d9a2 (Costa Rica, iterations 16)", "zoom 30cb73"]
---

## Description
PW-521's grading (zoom.FLOOR_SLOPE, kernels.grade_fills) fixes the flats that depression filling leaves.
It does not touch this one: in the Costa Rica zoom the 35,000 km2 coarse lake at 1718 m (landform
'glacial' 34.6% there) has a shore shelf of 4738 + 1331 + 1016 km2 of land at 1718-1747 m with slope
< 1 m/km, not a lake pixel and not a filled depression. It comes out of the landscape pass's lake rims
(`rims()`, `fl`/`cp`: land held at or just above the lake's level). A shelf like that reads as an
alluvial/lacustrine plain only if it slopes up from the shore; at the moment it is a table.
- [ ] grade the rim land up from the lake level (a few m/km) instead of holding it level
- [ ] re-measure: land cells > 300 m, not lake, slope < 1 m/km, area in 32d9a2 (7.4k km2 now)
