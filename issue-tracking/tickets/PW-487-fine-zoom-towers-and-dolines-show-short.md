---
id: PW-487
title: Fine-zoom towers and dolines show short hatched stripes at some edges
type: task
status: todo
parent: PW-516
milestone: v2
subsystem: zoom
effort: xs
impact: low
found_by: pw392-fine-forms
blocked_by: []
relates: [PW-392]
refs: [planet/zoom_fine_forms.py, planet/zoom_landforms.py, "zoom 7b0911 in dff894"]
created: 2026-10-20
updated: 2026-10-20
---

## Description
7b0911 (karst at 100 m, 435 towers and 38 dolines from zoom_landforms.Karst.overlay via Landforms.finish) shows a few tiny hatched stripes (alternate pixel rows) on the shaded relief at some tower and doline edges, ~10 pixels long. Probably the overlay's own per-pixel `blobs` edges meeting the 0.5 m floor, or the sub-pixel passes' interpolation of parent pixel means across a steep tower edge (zoom_fine_forms.subpixel, 4 passes). Check by rendering dz before and after subpixel().
- [ ] no striping at tower edges in a hillshade of 7b0911

## Updates
- 2026-10-20: Created from inbox draft draft-fine-zoom-karst-tower-hatching.md (found by pw392-fine-forms).
