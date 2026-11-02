---
id: PW-1344
title: "Notes for PW-1302 from lane 127: rivers across a matched section's owner line"
type: task
status: done
parent: PW-1299
milestone: v2
subsystem: zoom
effort: m
impact: high
found_by: lane127
blocked_by: []
relates: [PW-1302, PW-1301, PW-1338]
refs: ["planet/zoom/match.py::prepare", "planet/zoom/match.py::hold_edge", "planet/zoom/match.py::blend", "planet/zoom/stage_landscape.py::first_glaciers", "planet/zoom/stage_rivers.py::coarse_rivers", "planet/zoom/stage_landscape.py::final_drainage", docs/review/land-zoom/seams-round1.md, docs/review/land-zoom/practice.md, docs/review/land-zoom/seams.py]
created: 2026-11-02
updated: 2026-11-02
---

## Description
**In plain words.** Lane 127 made a section agree with a neighbour already built (PW-1301): the neighbour's ground is
held and the heights blend across an 80 km ramp. Rivers are not matched yet; this is what a PW-1302 lane needs to know.

- In a matched section the neighbour's ground is an outlet of the landscape pass (`match.hold_edge` adds it to
  `ctx.edge`), so the section's own rivers flowing towards the neighbour end at the owner line, at the neighbour's
  heights: their courses meet the neighbour's ground but their discharge is not handed on, and the neighbour (built
  first) never saw the water arriving from this side.
- Rivers flowing *from* the neighbour into this section are not brought in: the zoom already has an inflow mechanism
  for coarse rivers entering at the region's edge (`ctx.inflow_pts`, `stage_rivers.coarse_rivers`; the edge beside an
  inflow is made land). The neighbour's discharge where its rivers cross the owner line (its `discharge` layer, >= the
  river threshold) could become inflow points of this section with their course pinned in the held zone.
- Order matters: a river crossing several sections both ways needs either a second pass (rebuild the first section
  matched to the second) or a planet-wide routing of the coarse rivers' discharge that both sides read.
- Measure with `seams.py` river columns at the owner line (for tiling sections the cell edge, not the bisector).
- [ ] neighbour's crossing rivers enter the matched section as inflows with their discharge
- [ ] the matched section's rivers leaving across the line keep their discharge (stats) for the next section

## Updates
- 2026-11-02: Status todo -> done. Folded into PW-1302 (notes copied there).
- 2026-11-02: Created from inbox draft draft-land-zoom-matched-rivers-notes.md (found by lane127).
