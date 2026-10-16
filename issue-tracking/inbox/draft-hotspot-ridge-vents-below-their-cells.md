---
title: "Run: hotspot vents' recorded floor and top sit km below the cells they built (73.6N ridge on 592f2a)"
type: task
status: todo
parent: null
subsystem: tectonics
effort: s
impact: low
found_by: zoom-batch2
blocked_by: []
relates: [PW-310]
refs: [planet/tectonics/volcanism.py, "world:592f2a(73.6,121.0)"]
---

## Description
On world 592f2a near 73.6N 113-124E a chain of 6 hotspot vents (ages 0-6 Myr) has floor_m -3221 to
-4900 and eroded tops 1163-1530 m, while their coarse cells stand at 2300-3500 m (with 940-1300 m of
ice). The cells' heights come mostly from the vents' own crust (~13,000-37,000 km^3 each, 25 km radius,
spread over ~55 km cells), but the volcano table's floor sinks with an oceanic base level and its top is
eroded as an island; the cells' crust isn't eroded with it. So the table describes islands on a -4 km
floor where the run's cells are a 2-3 km plateau.

The zoom now copes (PW-310: the province lowers the ground only by the cones' share of each cell's mean,
so the plateau stays and the vents' summits are buried in it), but the two records disagree: a vent's
`floor` could follow its cells (the ground its neighbours built: min over its cell and neighbours, as at
birth, each step), or the cells could lose what the vent's erosion takes. Low priority; the zoom no longer
shows it as sea holes.
