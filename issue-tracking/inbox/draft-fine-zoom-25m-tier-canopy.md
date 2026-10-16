---
title: Is the 25 m fine zoom tier worth it (flat canopy, little gain over 50 m)?
type: task
status: needs-decision
parent: null
subsystem: zoom
effort: s
impact: med
found_by: pw129-fine-zoom
blocked_by: []
relates: [PW-129, PW-072]
refs: [planet/zoom_fine.py, "zoom 3e74b0", "zoom b3c260"]
---

## Description
I built the same 25 km square round the 822 m fall at 16.385, 155.723 at
50 m/px (zoom 3e74b0: 500 px, 5.6 s, 22 MB) and at 25 m/px (zoom b3c260:
1000 px, 17.8 s, 83 MB). Both are nested in the 100 m zoom 97b3e7.

Compared over the same 6 km, the 25 m view isn't meaningfully better. The
landforms are the same; the hillslopes get a little more texture. The gorge
artifacts are as visible (see the gorge banding draft). The canopy is a
smooth green colour field that follows the terrain shading. At 25 m one
pixel is one to three crowns, so a low 3D camera will see a flat, smeared
canopy. That is the threshold the owner flagged for canopy height or
instanced tree sprites.

Options:
- A. Keep 50 m as the finest default. Offer 25 m (1000 px) only as an option,
  and say in the UI that it's for close 3D views.
- B. As A, plus a canopy-height displacement in the 3D tile: the
  canopy_height layer is already in every zoom, so raise the forest surface
  20-40 m. This is cheap, and it reads as forest from a low camera.
- C. Instanced tree sprites in the 3D view at 25 m (one to three per pixel
  from tree_cover and canopy_height): the most convincing, but the most work,
  and it needs the 3D tile first.

Lean: A now, B with the 3D tile agent; C only if B still looks flat. More
pixels don't pay off until the gorge and reef forms are fixed at 50 m.
