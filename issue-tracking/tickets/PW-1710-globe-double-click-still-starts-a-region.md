---
id: PW-1710
title: "Globe: double-click still starts a regional zoom (a level change by click), against the Google Earth model"
type: task
status: done
parent: PW-1673
milestone: v1.0
subsystem: viewer
effort: s
impact: low
found_by: lane299
blocked_by: []
relates: [PW-1696, PW-1688]
refs: ["viewer/globe/pick.js::dblclick", viewer/globe/zoom.js, viewer/globe/dive.js, docs/review/zoom/lod-plan-v2.md, docs/review/zoom/lod-dive-299/06_ground_1km.png]
created: 2026-11-11
updated: 2026-11-11
---

## Description
**In plain words.** The globe now goes from orbit to the ground by scrolling, and tilts with a right-drag or
Shift-drag (PW-1688, PW-1696). Daniel's model is Google Earth: scroll to zoom, drag to pan, no clicks or double-clicks
to change level. But a double-click on the globe still picks the cell and starts a regional zoom
(`pick.js`: `dblclick` -> `pickCell` + `startZoom`), and the info box still says "click: copy and pick for zooming ·
double-click: zoom" even 1 km over the ground (`06_ground_1km.png`). If never decided, a stray double-click while
exploring builds a zoom and the hint teaches the old way.

Options:
- A. Remove the double-click zoom on the globe and the hint; the zoom tab and the picker keep making regional zooms.
- B. Keep it above the LOD range (orbit, where tiles are not drawn) and drop it below ~6,000 km, where scrolling does it.
- C. Keep it as is.

Lean: B (the globe at orbit is still where regional zooms are picked; low down it only gets in the way).

## Updates
- 2026-11-11: Status todo -> done. Merged lane 301.
- 2026-11-11: Status needs-decision -> todo. Coordinator ruled A (Daniel 11-10: 'nor do I like the idea of double click here to zoom'): remove the globe double-click zoom and its hint; the zoom tab and picker keep making regional zooms. Goes to the step-5 lane.
- 2026-11-11: Created from inbox draft draft-globe-double-click-starts-a-zoom.md (found by lane299).
