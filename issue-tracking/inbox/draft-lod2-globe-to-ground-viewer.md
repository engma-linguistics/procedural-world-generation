---
title: "LOD globe step 4: the globe camera goes down to the ground and draws level-1 and level-2 tiles on the sphere (fallback, fade, cell clipping)"
type: task
status: todo
parent: PW-1673
milestone: v1.0
subsystem: viewer
effort: l
impact: high
found_by: lane289
blocked_by: []
relates: [PW-1198, PW-1359, PW-1341, PW-415, PW-1360]
refs: [docs/review/zoom/lod-plan-v2.md, viewer/globe/scene.js, viewer/wheelzoom.js, "viewer/zoom3d_place.js::aeFrame", planet/zoom/lod.py, tools/viewer_perf_globe.py]
---

## Description
**In plain words.** Daniel wants to scroll from the whole planet down into detail like Google Earth, on the globe page, with
no clicking into separate zooms. Today the globe camera stops at 1.15 planet radii (~950 km up) and zooms open in another tab.
If this is not done, nothing of the on-demand detail can be seen. Plan: `docs/review/zoom/lod-plan-v2.md` section 4 (step 4);
can start alongside step 1, since level-1 sections are built by today's API (`POST /api/zoom {world, section, res_km: 4}`).
- Camera: zoom toward the cursor, minimum height from the ground under the camera, rotation slowing with height, tilt toward
  the horizon below ~200 km; near/far per frame; tiles placed relative to their centre (no float32 jitter at the ground);
  logarithmic depth only if it does not shimmer on Daniel's Chrome (PW-415).
- Tiles: a shared grid mesh displaced from the tile's elevation texture, placed through the cell's frame (`aeFrame`, the
  `lod.py` lattice), satellite colour and hillshade; fragments outside the cell dropped; a tile's built children drawn over
  it, the rest showing the tile stretched; fade-in on arrival; skirts against cracks.
- [ ] on a showcase world Daniel can scroll from orbit to ~1 km detail with tiles appearing and no camera jump (screen
      recording), 30+ fps, renderer memory measured with tools/viewer_perf_globe.py
