---
id: PW-345
title: "Zoom soils: one constant converts a pixel's slope to the cells' measure, but the zoom's roughness varies 4-22x"
type: task
status: done
parent: PW-184
milestone: null
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
- 2026-10-16: Status in-progress -> done. Done: pixel-slope exponent 0.3 above 2 km (measured, after PW-125's creep), 0.6 below; 4 km erosion ratio vs 2 km 1.4x -> 1.0x.
- 2026-10-16: Zoom batch 4: measured tools/zoom_soil_check on 7 400 km zooms of a1d3b9 @ 1000 Myr (keyframe world: plain, 2 plateaus, hills, range, dry, wet) at 4/2/1/0.5 km. Pixel/cell erosion ratio by region 0.27-1.09 at 1 km (the zoom's own roughness: option A kept). Across resolutions: 1 and 0.5 km are 0.75-1.6x the 2 km ratio (median 1.1): the 0.6 exponent holds finer than 2 km, so B isn't needed; 4 km was 1.1-2.1x (median 1.4) because a 4 km pixel's slope falls only as (2/res)^0.3 (measured 0-0.5, median 0.27: PW-125's creep makes it the mean of finer terrain). Fix: exponent 0.3 above 2 km (soils.PX_SLOPE_EXP_COARSE); 4 km now 0.7-1.4x (median 1.0), agreement on uniform/steep cells closer to 2 km's (plateau2 0.32 -> 0.44 vs 0.45). Option C (per-cell pull) not taken: the proposal avoided it.
- 2026-10-16: Status todo -> in-progress. Zoom batch 4 agent started.
- 2026-10-16: Created from inbox draft draft-zoom-soil-slope-scale.md (found by zoom-soils).
