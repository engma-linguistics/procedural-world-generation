---
title: Landscape pass leaves perfectly flat filled basins on high ground that spill over a rim into a deep valley
type: task
status: todo
parent: null
milestone: v2
subsystem: zoom
effort: m
impact: med
found_by: pw517
blocked_by: []
relates: [PW-517]
refs: [planet/zoom.py, "zoom 91486c at (107, 256)"]
---

## Description
Root cause of PW-517's 1186 m wall: a closed basin of the volcanic-arc landform sits at 1807 m (exactly flat over
~25 km, the depression filled to its spill) and its outlet river spills over the rim into a valley whose floor is
graded up from the sea (coast ramp 2 m/km, `coast_cap`; here 259 m at 35 km inland), so the river drops ~1.5 km in
3 px. No designed fall is involved (Q 49 m3/s is under KP_MIN_Q 100; `kind: drop`). PW-517 shapes the drop afterwards
(zoom_falls.carve) and cuts the gorge into the basin, but the flat fill itself is not physical: a basin on a
mountain would have been drained by headward incision long before, or be a lake with a shore. Look at why
the pass fills it flat (the pit fill in the final drainage, `h = max(h, filled)`) and whether the basin should
instead be a lake (zoom_landforms basin_lakes) or drained by the gorge.
- [ ] list flat filled areas > 50 km2 over 500 m above their outlet in the showcase zooms
