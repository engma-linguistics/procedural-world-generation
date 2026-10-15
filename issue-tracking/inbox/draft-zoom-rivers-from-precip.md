---
title: Zoom discharge routes precipitation, not runoff, so hyper-arid zooms draw rivers
type: task
status: todo
parent: null
subsystem: zoom
effort: s
impact: med
found_by: zoomland3
blocked_by: []
relates: [PW-012]
refs: [planet/zoom.py, "zoom:e14044", "zoom:2d1537"]
---

## Description
zoom.build's water source is `srcq = precip / 1000 * res^2 + inflow`
(precipitation, not the world's `runoff` = precipitation - actual
evaporation). In a 40-80 mm/yr desert (the ergs around -29, -9 on
a08983) the zoom then drew 100-300 m3/s rivers across the dune field;
batch 3 now lets streams under 30 m3/s end in the sand (Dunes.sinks), but
the same overestimate holds in every dry zoom (semi-arid hills, steppe):
too many, too big rivers, and the steady-state landscape pass incises by
that discharge. The coarse world's rivers use runoff.
Try: route runoff (interpolated like precipitation; the basin water
balance in zoom_landforms.basin_lakes already reads it), keeping
precipitation only where the world lacks the layer; check falls, cell
means and the delta discharges don't move much in wet zooms.
- [ ] a 50 mm/yr zoom has no river it doesn't get from outside
