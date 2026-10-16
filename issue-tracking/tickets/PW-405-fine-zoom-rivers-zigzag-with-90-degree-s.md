---
id: PW-405
title: Fine zoom rivers zigzag with 90-degree switchbacks every ~100 m; planform should follow slope, confinement and sediment
type: task
status: todo
parent: null
subsystem: zoom
effort: m
impact: high
found_by: daniel
blocked_by: []
relates: [PW-129, PW-390, PW-391, PW-403]
refs: [planet/zoom_fine.py, viewer/zoom3d.js]
created: 2026-10-16
updated: 2026-10-16
---

## Description
Owner on b3c260 (25 km @ 25 m, below the 822 m fall): the river below the gorge makes several tight switchbacks within ~0.1 km, with right-angle elbows, in a steep bedrock valley. That would be plausible as meanders over miles on a low-gradient floodplain, but not here.

Coordinator diagnosis: two causes.
- **Artifact.** Outside the imposed gorge, the fine river is the D8 path of the fine landscape pass on a noised surface: 45/90-degree steps plus wander between noise bumps. The 3D river line also follows D8 receivers (the zigzag noted in PW-390). The parent's noise-warped polyline is not used as the channel there.
- **Missing physics.** Channel planform isn't chosen from conditions at all. Real rivers follow:
  - Steep, confined bedrock channels: nearly straight along the valley axis, with bends only at valley scale.
  - Low-gradient alluvial channels (gentle slope, soft rock or thick sediment, wide valley floor): meanders with wavelength ~10-14 channel widths (w ~ 4 Q^0.5 m: ~25 m wide at 36 m3/s, so ~300 m wavelength) and amplitude limited by the valley floor's width.
  - High sediment load with steep fans: braided.

Fix:
- Carve fine channels along a smooth centreline (as PW-390 does for gorges), not D8 pixels.
- Choose the planform per reach from slope, discharge, valley-floor width and rock/sediment (surface_rock, soil depth, alluvial share): straight-ish bedrock, meandering alluvial, braided.
- Draw the 3D river line along the same centreline.
- Test: sinuosity and minimum bend radius (>= ~2-3 widths) per planform class.

## Updates
- 2026-10-16: Created from inbox draft draft-fine-zoom-river-planform.md (found by daniel).
