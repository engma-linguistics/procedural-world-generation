---
title: "Zoom preview.png and relief layer still tint by rain; tint by the zoom's vegetation (with PW-083's satellite colours)"
type: task
status: todo
parent: null
subsystem: zoom
effort: s
impact: med
found_by: vegzoom
blocked_by: []
relates: [PW-083, PW-214]
refs: [planet/zoom.py, viewer/zoom.html]
---

## Description
Zooms now carry per-pixel vegetation (PW-214: vegetation, tree_cover, plant_cover, lai), but `zoom.preview()` (and so the viewer's default Relief layer) still colours land by a wet/dry ramp on precipitation and height (`tint`). Gallery forests, treelines on sunny and shaded slopes and mire mosaics only show on the Vegetation and Tree cover layers. With the satellite colouring of PW-083 / PW-187 step 9 (sum of fraction x PFT colour x greenness, bare ground by rock, snow), the preview could use tree cover, plant cover and LAI per pixel; until then a simple blend (tree cover darkens and greens the tint, plant cover under 20% shows the bare-ground colour) would already help.
- [ ] preview.png tinted by the zoom's vegetation
