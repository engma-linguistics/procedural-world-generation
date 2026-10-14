---
id: PW-161
title: "Zoom viewer: show glaciers on the relief and hillshade layers"
type: task
status: todo
parent: null
subsystem: viewer
effort: xs
impact: med
found_by: zoomice
blocked_by: []
relates: [PW-127]
refs: [viewer/zoom.html, "zoom d2a1d5"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
The zoom viewer shows the `ice` layer only through the biome view (ice sheet = glaciers since PW-127); the relief view's white is the hypsometric tint of high ground, not ice, so glaciers, ice-free high plateaus and valley tongues can't be told apart there (zoom d2a1d5: the relief view looks snow-capped everywhere above ~3 km, the biome view shows the actual icefields). Tint `ice > 0` pixels blue-white on relief/hillshade, as zoom.preview() does, and maybe add an Ice layer button (thickness).

## Updates
- 2026-10-14: Created from inbox draft draft-zoom-viewer-relief-ice.md (found by zoomice).
