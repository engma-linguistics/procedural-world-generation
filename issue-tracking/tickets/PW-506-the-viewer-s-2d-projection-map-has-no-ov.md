---
id: PW-506
title: The viewer's 2D projection map has no overlays, relief shading or zoom-tab version
type: task
status: todo
parent: null
milestone: null
subsystem: viewer
effort: m
impact: low
found_by: viewer-batch
blocked_by: []
relates: [PW-477]
refs: [viewer/projmap.js, "viewer/index.html (drawProj)"]
created: 2026-10-21
updated: 2026-10-21
---

## Description
The 2D map mode (PW-477, viewer/projmap.js) paints the current layer's flat cell colours into the projection, plus a graticule and a centre mark. Missing:
- Overlays the globe has: rivers, plate outlines, hotspots/volcanoes, highlight markers, the zoom outlines (clicking one could open the zoom). They need the same forward projection applied to their lat/lon polylines (`makeProjection(...).forward` is ready; draw on the 2D canvas, cut lines at the seam as `graticule` does).
- Hill shading for the satellite and elevation layers (the flat Map mode has `mapHillshade`; the projected map is flat colour).
- Smoothing: pixels take the nearest cell's colour, so a level 4-6 world shows the hexagons at regional extents (the `smooth` checkbox is ignored); interpolating between the 3 nearest cells would match the globe's smooth mode.
- The regional zoom tab (zoom.html) has no projected map; zooms can be exported with `planet export --projection` only.
- No scale bar or lat/lon readout under the pointer (the hover box shows the cell only).
- [ ] rivers, outlines and markers on the map
- [ ] smooth colours at regional extents

## Updates
- 2026-10-21: Created from inbox draft draft-map2d-overlays.md (found by viewer-batch).
