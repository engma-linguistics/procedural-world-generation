---
title: "Zoom: draw the bed below sea level under grounded ice (it still takes it at 1 m)"
type: task
status: todo
parent: PW-090
subsystem: zoom
effort: m
impact: low
found_by: pw307-world-land
blocked_by: []
relates: [PW-307, PW-197, PW-189]
refs: [planet/zoom.py, planet/tectonics/isostasy.py]
---

## Description
Since PW-307 worlds store the true bed under grounded ice and treat it as land (`geo.is_land`). The
regional zoom's pixels are land where their ground is above the sea (`h > 0`, the coarse land
interpolant floored at 1 m, glaciers on land), so `zoom.zoom_world` hands it the world with such a
bed at 1 m and the ice thinned to keep the surface (`isostasy.land_view`, the floor worlds had
before). The coastline and the ice surface are right; the bed under a marine sheet or a deep
isostatic dip is drawn at ~1 m instead of down to -1500 m (time zoom 080df3 at 950 kyr: 2564 L7
cells, bed -349 m mean), so a zoom's bed-under-ice view and any sub-ice lake are wrong there.
Fix: let a zoom pixel be land by its ice too (h <= 0 under glacier ice), interpolate the coarse
land bed without the 1 m floor where the cell is iced, and keep the glacier model and the water
layer from calling those pixels sea; then drop `zoom_world`.
- [ ] a zoom over a marine sheet keeps the world's sub-sea bed under its ice, no sea pixels there
- [ ] `zoom_world` removed
