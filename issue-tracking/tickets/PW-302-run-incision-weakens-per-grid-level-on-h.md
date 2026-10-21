---
id: PW-302
title: Run incision weakens per grid level on headwater cells (2.2 / 1.6 / 1.1 m per step, L5 / L6 / L7)
type: task
status: wontdo
parent: PW-245
milestone: v1
subsystem: surface
effort: s
impact: low
found_by: surface-hydro
blocked_by: []
relates: [PW-282, PW-243]
refs: [planet/surface.py, docs/review/audit/fixes-surface-hydro.md]
created: 2026-10-15
updated: 2026-10-15
---

## Description
After PW-282 the run's hillslope term is level-consistent (synthetic continent, one 2-Myr step, mean land
lowering 2.49 / 2.51 / 2.50 m at L5 / L6 / L7). The stream-power incision term is not: 2.23 / 1.61 / 1.14 m on
the same terrain (the audit measured 2.38 / 1.56 / 1.04 before PW-282). This is not a mislabelled law:
`stream_power`'s rate ~ sqrt(flow in cells x m/yr) x drop is Braun & Willett's sqrt(A) x slope in disguise
(flow ~ A / cell area, drop ~ slope x d ~ slope x sqrt(cell area)), so a given catchment cuts the same at any
level. It falls because a finer grid has more small-catchment cells: a cell that drains only itself drains a
quarter of the area at each finer level, so it cuts half as fast. The coarse grid overstates the river cutting
of headwater cells (it lends them a whole cell's catchment); the finer grid shows sub-cell wear only through
the hillslope term. Total lowering is now 9.4 / 8.8 / 8.3 m per step (was 8.2 / 8.8 / 10.7), within PW-282's
20%, so this is a second-order level difference.
Options: leave it (lean: the law is sound; what differs is what the cells resolve); or give headwater cells a
sub-cell channel term (an extra hillslope-like share for cells with little upstream area), which would be a
new parameterisation to calibrate. Worth keeping in mind for PW-243's L6/L7 closed-basin gap.

## Updates
- 2026-10-15: Status needs-decision -> wontdo. Owner 2026-10-15: leave it; the law is sound. Findings carried to PW-054.
- 2026-10-15: Created from inbox draft draft-incision-level-consistency.md (found by surface-hydro).
