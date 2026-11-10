---
title: An L8 refine's soils are thinner and peatier than its L7 world's, so its farmland is 11% poorer (slope read over the node spacing)
type: task
status: todo
parent: PW-1198
milestone: v5
subsystem: surface
effort: m
impact: med
found_by: lane272b-pw1631
blocked_by: []
relates: [PW-1631, PW-1630, PW-1265, PW-1584]
refs: ["planet/soils.py::erosion_rate", "planet/soils.py::cell_slope", "planet/soils.py::zoom_slope", "planet/humanuse.py::fertile", "planet/humanuse.py::slope_deg_net", docs/review/refine-l8/split.md, "world 899985 (Earth-like A, L7)", "world 9cf1c3 (899985 refined to L8, lane 272 scratch, may be gone)", "fert_diag.py and slope_diag.py (lane 272 scratch)"]
---

## In plain words
When a world is refined from L7 to the finer L8 grid, the refined world's soils come out thinner and boggier, though it is
the same land. Its farmland is about a tenth poorer, so every L8 world feeds fewer farmers and has fewer coastal towns
than the same world on L7. Readers will take that as a fact about the world when it comes from the grid.

## Description
Earth-like A: world 899985 (L7) against its L8 refine 9cf1c3, land means (split.md section 7, `fert_diag.py`):
- humanuse fertile class 0.971 (L7) against 0.868 (L8), -11%; within 60 km of the sea the fertile good is 0.539 against
  0.439;
- soil depth mean 1.31 against 0.99 m (25th percentile 0.56 against 0.10 m); peat over 0.5 m on 31.5% against 40.1% of
  the land;
- with peat ignored the classes are 1.376 and 1.431; with the depth floored at 1 m, 1.06 and 1.075. So these two layers
  carry the whole gap. The slope term in humanuse.fertile removes under 0.1% on either grid.
Likely cause: soils.erosion_rate goes as the square of soils.cell_slope (relief over grid.spacing), and the finer grid
resolves steeper slopes, so erosion is higher and soils thinner. The zoom path already corrects a pixel's slope to the
cells' measure (soils.zoom_slope, PX_SLOPE); the world path has no such correction for a refine. The peat rise is not
traced yet (wetter flats, or the same slope read).
In the peoples' model this was about half of the split history's 12-14% people gap (PW-1631; the other half, the
irrigated valley, is fixed by lane 272).
- [ ] read the slope for soils at a fixed scale (the L7 cell's, as zoom_slope does for pixels), or show why the L8 soil is right
- [ ] re-check fertile class, soil depth and peat on 9cf1c3 (or a fresh refine) against 899985
