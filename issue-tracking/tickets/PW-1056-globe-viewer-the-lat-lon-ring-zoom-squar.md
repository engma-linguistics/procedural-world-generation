---
id: PW-1056
title: "Globe viewer: the lat/lon ring, zoom square and arrow-head code is still copied 2-5 times; share it in globe/draw.js"
type: task
status: todo
parent: null
milestone: null
subsystem: viewer
effort: s
impact: low
found_by: viewer-lane-51
blocked_by: []
relates: [PW-1045, PW-685]
refs: [viewer/globe/draw.js, viewer/globe/overlays.js, viewer/globe/highlights.js, viewer/globe/zoom.js, viewer/globe/geometry.js, viewer/projmap.js]
created: 2026-10-30
updated: 2026-10-30
---

## Description
In plain words. Some drawing code on the globe is still copied in several places. That code draws circles round a place, the outline of a zoom region, and the heads of the wind and plate arrows. A fix to one copy (for example, how a circle behaves where it crosses the date line) won't reach the others. The module split moved this code but didn't merge it, because merging is a separate step that needs its own before/after check.

The copies (viewer-code audit finding 12):
- **The circle of radius r degrees round a lat/lon** (cos-lat corrected, skipping date-line wraps). It appears in:
  - events (overlays.js)
  - highlights (highlights.js)
  - people origins (overlays.js)
  - the zoom square, twice and identical (`buildOverlays` and `buildZoomOutlines`)
- **`wraps`** is defined 4 times, and `Math.max(Math.cos(lat), 0.1|0.2)` appears about 11 times.
- **Arrow heads.** `flowArrows` and the plate arrows hold the same globe/map arrow-head code.
- **`toThree`** is defined in geometry.js, while projmap.js exports the same function.

Fix:
- Add `ring(lat, lon, r, …)`, `zoomSquare(…)` and `arrowHead(…)` to globe/draw.js, next to `canvasSprite`.
- Use projmap's `toThree`.
- Check with a screenshot comparison of the overlays (events, highlights, zoom outlines, winds, plates), on globe and map, before and after.

Related cleanups to the same code that already have owners:
- Sprite caching and the cloud-texture dispose: PW-1045.
- Hoisting per-cell lookups (pftColor, resColor, cropBit) out of the colour loops: PW-1045, and later PW-685. The new `color` factories in layers.js are where that hoisting goes.

## Updates
- 2026-10-30: Created from inbox draft draft-globe-draw-helpers.md (found by viewer-lane-51).
