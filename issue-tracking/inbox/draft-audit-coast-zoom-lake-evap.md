---
title: "Zoom coarse lakes: no open-water evaporation; lake pixels yield land runoff"
type: task
status: todo
parent: PW-245
subsystem: zoom
effort: xs
impact: low
found_by: audit-coast-zoom
blocked_by: []
relates: [PW-060]
refs: [planet/zoom.py, planet/zoom_landforms.py, docs/review/audit/coast-zoom.md]
---

## Description
In `zoom.build`, `srcq` (zoom.py:1636) gives lake pixels the interpolated land runoff. `route` (1881-1889)
then passes an open lake's whole `sum(q)` on at its outlet. The lake's net open-water evaporation is never
taken off, though `zoom_landforms.basin_lakes` does take it off for landform basins (and the coarse world
does for its own lakes). So a big open lake's outflow in the zoom is too high relative to the parent world.

Fix: on coarse-lake pixels, use rain minus open-water evaporation (the `fv` loss field already built for
basin_lakes, zoom.py:2227-2232) instead of land runoff, and subtract it from the lake's total before
passing it on (floor at 0).
- [ ] an open zoom lake's outflow within ~10% of the coarse lake's outflow (when the catchment is in view)
