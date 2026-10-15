---
id: PW-180
title: Zoom discharge routes precipitation, not runoff, so hyper-arid zooms draw rivers
type: task
status: done
parent: null
subsystem: zoom
effort: s
impact: med
found_by: zoomland3
blocked_by: []
relates: [PW-012]
refs: [planet/zoom.py, "zoom:e14044", "zoom:2d1537"]
created: 2026-10-14
updated: 2026-10-14
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

## Updates
- 2026-10-14: Status todo -> done. Zoom streams carry the world runoff (land-weighted interpolation; precipitation only if a world lacks runoff); the landscape pass, creep and landform valleys keep the rain-weighted drainage area (else a desert with ~0 runoff has no graded network: cell-mean RMS 27 -> 227 m). Desert zooms: e14044 66 -> 8 px >= 3 m3/s (only the stream entering from outside, ending in the sand), 2d1537 127 -> 12. Wet/savanna: f9b027 maxQ 318 -> 172, falls 42 -> 40; 83e518 falls 27 -> 30; 2d06f8 (savanna, runoff 17% of rain) maxQ 2946 -> 534, falls 15 -> 6; 130acd falls 21 -> 9; delta discharges and cell means unchanged. WF_MIN_Q 50 -> 20, GORGE_Q 100 -> 30 m3/s; other thresholds in an inbox draft (zoompolish).
- 2026-10-14: Created from inbox draft draft-zoom-rivers-from-precip.md (found by zoomland3).
