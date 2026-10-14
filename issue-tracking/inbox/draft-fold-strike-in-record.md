---
title: Record the fold strike (shortening direction) so fold belts don't guess it from crust thickness
type: task
status: todo
parent: PW-005
subsystem: tectonics
effort: m
impact: med
found_by: zoomland2
blocked_by: []
relates: [PW-011, PW-008]
refs: [planet/zoom_landforms.py, planet/tectonics/record.py, "world 800c99", "zoom 516580"]
---

## Description
The zoom's fold belt (zoom_landforms.FoldBelt) needs the fold axes'
direction. The world carries none, so build_frames reads it per ~200 km
patch from the coarse cells around it: the trend of crust thickness and of
the high ground (structure tensors over ~4 cells) and a converging boundary
if one is near. On world 800c99 these cues are weakly coherent (coherence
~0.05-0.15 at the fold belt at -38.1, 9.3: thickness ~50-60 deg, elevation
~50-57 deg, boundary ~46 deg, so they agree there), and patch strikes still
scatter by +-30 deg; old belts far from any boundary have only the
thickness left, which erosion and isostasy blur.

Try: when the record marks a cell folded (record.T_FOLD), also store the
direction of the relative plate motion across the converging boundary that
folded it (or the gradient of the thickening in that step), rotated with the
plate, as a strike angle; slice it as a landform layer (`fold_strike`) and
let build_frames use it as the main cue. Same idea for rifts (stretching
direction), which now use the long axis of the rift's band of cells.
