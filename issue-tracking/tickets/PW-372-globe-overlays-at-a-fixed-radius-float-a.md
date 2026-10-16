---
id: PW-372
title: Globe overlays at a fixed radius float above or sink into the 3D relief
type: task
status: in-progress
parent: null
subsystem: viewer
effort: s
impact: low
found_by: viewer-3d
blocked_by: []
relates: []
refs: [viewer/index.html, viewer/relief.js, "run a1d3b9", "world bd9a7a"]
created: 2026-10-16
updated: 2026-10-16
---

## Description
With the globe's 3D relief on (`&relief3d=1`, default 50x), rivers and cell outlines sit on the
relief (`cellPositions`, `V.R`), but the overlays drawn with `llPos(lat, lon, r0)` at a fixed
radius don't: volcano triangles and atoll rings (r0 1.012), hotspot circles (1.012), event markers
(1.01), the zoom box (1.014), highlight marks (1.016). At 50x, 1.012 is ~1500 m: they float over
lowlands and sea and are buried under high ground and ice sheets (a 3 km sheet is ~1.024; seen on
run a1d3b9 at 500 Myr and world bd9a7a). On the flat map's relief (`mode=map`) they lie at z = 0
under the raised land.

Fix: give `llPos` the relief height of the nearest cell (or of the overlay's own cell, which most
callers know) plus a small lift, as `cellPos` does. Left alone on the viewer-3d branch because
another agent was changing the volcano and highlight overlays at the same time.
- [ ] volcanoes, hotspots, events, zoom box and highlight marks sit on the relief on globe and map

## Updates
- 2026-10-16: Status todo -> in-progress. Small fixes batch agent started.
- 2026-10-16: Created from inbox draft draft-relief-overlays-fixed-radius.md (found by viewer-3d).
