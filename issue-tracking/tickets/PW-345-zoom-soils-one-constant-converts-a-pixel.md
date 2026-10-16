---
id: PW-345
title: "Zoom soils: one constant converts a pixel's slope to the cells' measure, but the zoom's roughness varies 4-22x"
type: task
status: todo
parent: PW-184
subsystem: zoom
effort: s
impact: low
found_by: zoom-soils
blocked_by: []
relates: [PW-331, PW-185]
refs: [planet/soils.py, tools/zoom_soil_check.py]
created: 2026-10-16
updated: 2026-10-16
---

## Description
Zoom soils (PW-331) run the world's erosion law, which is written in the cells' measure (m per km to the steepest
neighbour, 55-110 km away), on each pixel's own slope converted by `soils.zoom_slope`: tan x 1000 / PX_SLOPE (10 at
2 km), finer pixels steeper by (2 km / res)^0.6. Measured with `tools/zoom_soil_check.py` on seven 400 km zooms of two
L7 worlds, a pixel's RMS slope is 4-22x its cell's (a dissected plateau 4x, a dry range 15x, a gentle plain 22x), and
the exponent between 4 and 0.5 km pixels 0.3-0.8 depending on the region. So where the zoom's terrain is smoother than
the cells' relief (the plateau, cells 6-8 m/km), its pixels erode less and carry older soils (red clay) than their cells
(young brown), 1-34% agreement; on a gentle plain the pixels erode ~3.5x more than the cell.

Options: (A) keep the constant (sound on average, differences are the zoom's own terrain); (B) measure each pixel's
slope over a fixed baseline (e.g. the terrain smoothed to ~4 km) so it no longer depends on the resolution, then
recalibrate one constant; (C) per zoom, scale the pixels' slopes so each cell's mean erosion matches the cell's (a pull
towards the coarse cell, which the proposal avoided). Lean A unless zooms look wrong; B if 0.5 km zooms do.

## Updates
- 2026-10-16: Created from inbox draft draft-zoom-soil-slope-scale.md (found by zoom-soils).
