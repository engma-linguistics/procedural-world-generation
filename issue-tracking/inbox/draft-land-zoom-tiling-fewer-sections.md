---
title: Land zoom tiling: 47 sections for dba204 land; cut it by covering land, not cells
type: task
status: todo
parent: PW-1299
milestone: v2
subsystem: zoom
effort: s
impact: med
found_by: lane122
blocked_by: []
relates: [PW-1319, PW-1303]
refs: ["planet/zoom/tiling.py::sections", "planet/zoom/tiling.py::margin_km", docs/review/land-zoom/tiling.md, docs/review/land-zoom/cost.md, "world dba204"]
---

## Description
**In plain words.** The cube cut is fixed, so dba204's land (36% of the sphere) needs 47 of 54 sections (99.6% of land cells), against
~12 squares of pure land area. At ~16 min per 1 km section that is ~12 h of compute. Ideas: (1) keep a cell only if
its land is not already inside a neighbour's square with margin (greedy set cover over land cells, using the section planes);
(2) rotate the whole cube (try a few orientations) to put the fewest land cells near cell edges, or to put
the thin-land cells (ice caps, small islands) together; (3) merge cells with < 10% land into a neighbour by giving that
neighbour a bigger square (<= 5000 km, 1.2 km/px at 4096 px). Check each choice keeps >= 97 km of margin over land.
- [ ] a `sections(world, cover="land")` mode and the section count for dba204 and 2-3 other worlds
- [ ] decide with the owner how much overlap is needed when the seam fix lands (PW-1301/1302)
