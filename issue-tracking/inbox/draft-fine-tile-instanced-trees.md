---
title: Instanced trees on 25-50 m fine tiles in the zoom 3D view (canopy displacement isn't enough)
type: task
status: todo
parent: null
subsystem: viewer
effort: m
impact: med
found_by: fine-zoom-3d
blocked_by: []
relates: [PW-388, PW-129, PW-072]
refs: [viewer/zoom3d.js, "zoom b3c260", docs/review/fine-zoom-3d/canopy_25m_low_on.png, docs/review/fine-zoom-3d/canopy_25m_low_off.png]
---

## Description
PW-388 option B is built: on tiles of 100 m/px or finer, forested pixels stand up
by canopy_height x smoothstep(10, 60, tree_cover), with a fixed +-30% per-pixel
jitter, not on rivers, water or ice (Tile.surface, "canopy" checkbox). Seen from
120 m above b3c260 (25 m/px), it gives the forest a rough skin, an edge and a
ragged skyline, but the near slope still reads as a lumpy green carpet, not
trees (compare the on/off screenshots). At 50 m from a moderate height it reads
as forest well enough.

Option C would fix it: instanced crowns (a cone or billboard per tree, 1-3 per
pixel at 25 m from tree_cover, height from canopy_height, colour from the
satellite texture), only within a few km of the camera, on top of the
displaced canopy. ~100k-500k instances at 25 m in view; cheap on this GPU with
instancing and a distance cut-off.
- [ ] trees within ~3 km of the camera on tiles <= 50 m/px, culled beyond
- [ ] a low-camera screenshot at 25 m that reads as forest
