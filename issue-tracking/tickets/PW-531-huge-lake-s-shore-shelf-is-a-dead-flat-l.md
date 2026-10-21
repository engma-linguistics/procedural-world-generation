---
id: PW-531
title: Huge lake's shore shelf is a dead-flat land plain (4700 km2 at 1718-1747 m in the Costa Rica zoom)
type: task
status: done
parent: null
milestone: v1
subsystem: zoom
effort: m
impact: med
found_by: pw522
blocked_by: []
relates: [PW-521]
refs: [planet/zoom.py, "zoom 32d9a2 (Costa Rica, iterations 16)", "zoom 30cb73"]
created: 2026-10-21
updated: 2026-10-21
---

## Description
PW-521's grading (zoom.FLOOR_SLOPE, kernels.grade_fills) fixes the flats that depression filling leaves.
It does not touch this one: in the Costa Rica zoom the 35,000 km2 coarse lake at 1718 m (landform
'glacial' 34.6% there) has a shore shelf of 4738 + 1331 + 1016 km2 of land at 1718-1747 m with slope
< 1 m/km, not a lake pixel and not a filled depression. It comes out of the landscape pass's lake rims
(`rims()`, `fl`/`cp`: land held at or just above the lake's level). A shelf like that reads as an
alluvial/lacustrine plain only if it slopes up from the shore; at the moment it is a table.
- [x] grade the rim land up from the lake level (a few m/km) instead of holding it level
- [x] re-measure: land cells > 300 m, not lake, slope < 1 m/km, area in 32d9a2 (7.4k km2 now)

## Updates
- 2026-10-21: Fixed on branch worktree-agent-a26968755bf8de897 (pw531). Cause: the slope fit keeps each coarse cell's mean and the cell beside a lake lies only ~30 m above it, so the fit leaves a plain of ~1 m/km 30 km wide (not rims(), which holds only the 1-px ring). `zoom.shore_apron` + `ZK.raise_to_run` now lift land within a big lake's reach (0.6 x sqrt(area), <= 40 km; lakes >= 150 km2) to rise >= 2 m/km after a ~1 km beach, off rivers (>= 20 m3/s) and the held rims/rapids/falls courses; nothing is lowered, drainage and lake levels untouched. Costa Rica (same code, 18 iterations): land > 300 m, slope < 1 m/km 8002 -> 1554 km2 (zoom f24fda); lake 38417 km2, level 1696.5 m unchanged. Other zooms: no change where no coarse lake >= 150 km2 (Baltic, Labrador) and none needed in the Alps one. Remainder: draft-flat-basin-and-landform-lake-shores.
- 2026-10-21: Created from inbox draft draft-lake-shore-plains-flat.md (found by pw522).
