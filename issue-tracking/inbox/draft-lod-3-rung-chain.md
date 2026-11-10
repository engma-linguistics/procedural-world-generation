---
title: "Zoom rungs under a 4,000 km section: measure and judge 500 km at 0.5 km and 30 km at 25 m made by the fine pass"
type: task
status: todo
parent: PW-1198
milestone: v1.0
subsystem: zoom
effort: m
impact: high
found_by: lane282
blocked_by: []
relates: [PW-1299, PW-516, PW-541, PW-485, PW-129]
refs: [docs/review/zoom/lod-plan.md, "planet/zoom/fine.py::default_size", "planet/zoom/fine.py::check", "planet/zoom/fine.py::zoom", docs/proposals/nested_fine_zoom.md, docs/review/land-zoom/cost.md, "planet/zoom/tiling.py::section", "world dba204"]
---

## Description
**In plain words.** The level-of-detail flow (plan `docs/review/zoom/lod-plan.md`, step 2) goes section (4,000 km at
2 km/px) -> rung 1 (~500 km at 0.5 km, a 4x step) -> rung 2 (~30 km at 25 m, 20x), both by `zoom.fine`, which keeps the
parent's heights and rivers. Fine zooms have only been made at ~25-100 km from 0.1-2 km parents; a 500 km fine zoom from
a 2 km parent is allowed by `fine.check` but never made, and the fine pass does not redraw landform overlays, glaciers,
deltas or reefs (nested_fine_zoom.md), so rung 1 may read as a sharpened copy of the section. `fine.default_size`
assumes a 20x step. If never done, the viewer work builds on rung sizes nobody has looked at, and the owner may find
the middle level empty.

On one land section of a v1.0 showcase world at 2 km (CLI, own scratch data root, <= 8 cores, by day only 2 km):
- [ ] rung 1 and rung 2 at three places (a mountain range, a river plain, a coast): wall time, peak RAM, disk per rung
- [ ] parent-mean bias and river continuity at each rung's edge; pictures of each rung beside its parent
- [ ] rung 1 compared with a regional 500 km zoom at 0.5 km of the same spot: what the fine pass lacks
- [ ] `fine.default_size` (and the viewer's size menu rules) give the rung sizes for 0.5-4 km parents
- [ ] `docs/review/zoom/lod-rungs.md` with a yes/no on rung 1; a "no" goes to Daniel as the plan's question Q3 with the pictures
