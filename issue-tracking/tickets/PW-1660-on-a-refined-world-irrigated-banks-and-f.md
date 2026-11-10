---
id: PW-1660
title: On a refined world, irrigated banks and floodplains are a share of a river's own cells, so they halve at L8 and cost the fertile class ~1.3 points
type: task
status: todo
parent: PW-1198
milestone: null
subsystem: surface
effort: s
impact: med
found_by: lane274
blocked_by: []
relates: [PW-1584, PW-1265]
refs: ["planet/humanuse.py::IRRIGATE_Q", "planet/humanuse.py::fertile", "planet/vegetation.py::floodplain", "planet/vegetation.py::cell_relief", "planet/soils.py::mineral", docs/review/refine-l8/soils.md, "world 899985 (Earth-like A, L7)", "lane 274 scratch: ed3e56 (899985 re-finished at L7), 108b4f (L8 refine, lane 274 branch); deleted after the lane"]
created: 2026-11-10
updated: 2026-11-10
---

## In plain words
Big rivers water the farmland along their banks, and their floodplains lay down rich silt. The model gives both only to
the cells the river runs through. On a finer grid the river's line of cells covers half as much land, so a refined
world has half the watered banks and half the floodplain of its own L7 world. The land is the same, but the people on
the refined world find less good farmland.

## Description
Lane 274 fixed the soils' slope on a refine (soil depth, `vegetation.cell_relief`). What is left of the L8 fertile
gap on Earth-like A (899985) is mostly the river line. The baseline is 899985 re-finished at L7 with today's code
(ed3e56), against its L8 refine on the lane 274 branch (108b4f):
- `humanuse` irrigates a cell whose own discharge is ≥ `IRRIGATE_Q` (100 m³/s). That is 43.3% of land at L7 and
  18.3% at L8. Without irrigation the fertile class means are 0.972 and 0.951; with it they are 1.003 and 0.965. The
  banks are ~1.3 of the 3.8 points of the remaining gap, and more along the coasts, where the rivers end.
- `vegetation.floodplain` gives a river cell a *share* of itself (0–0.35 by discharge), not a width in km. Floodplain
  covers 1.37% of land at L7 and 0.74% at L8. It feeds the soils' alluvium (fertile silt, and no peat on the active
  floodplain) and the flooded share.

What breaks if never done: every refined world (the split pipeline's L8 history) has less farmland near big rivers
than its own L7 world, so peoples' densities and town siting along rivers differ for grid reasons alone (PW-1584's
class of problem).

Try: give the banks and floodplain a width in km. Irrigation could reach cells within ~CELL_KM / 2 of a ≥100 m³/s
channel. The floodplain share could be the width (share × CELL_KM at L7) over the cell's own size, with the excess
spread to the neighbouring cells. At L7 and coarser this must be exactly today's numbers.
- [ ] L7 world bit-identical
- [ ] L8 refine of 899985: irrigated and floodplain shares of land within 10% of ed3e56's

## Updates
- 2026-11-10: Created from inbox draft draft-river-line-shares-halve-on-refine.md (found by lane274).
