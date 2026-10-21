---
id: PW-405
title: Fine zoom rivers zigzag with 90-degree switchbacks every ~100 m; planform should follow slope, confinement and sediment
type: task
status: done
parent: null
subsystem: zoom
effort: m
impact: high
found_by: daniel
blocked_by: []
relates: [PW-129, PW-390, PW-391, PW-403]
refs: [planet/zoom_fine.py, viewer/zoom3d.js]
created: 2026-10-16
updated: 2026-10-21
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
- 2026-10-21: Status todo -> done. Merged 59dea9e (2026-10-16); closed by coordinator 2026-10-21. Check it in the PW-202 showcase remake, since the old zooms are being deleted.
- 2026-10-16: Created from inbox draft draft-fine-zoom-river-planform.md (found by daniel).
- 2026-10-16: Implemented on branch worktree-agent-a77223c7eaa43cc01 (pw405).
  - Cause: the fine course was a Catmull-Rom through the parent's D8 pixel centres, plus a 2-parent-px noise warp. A fine parent's receivers are D8 at 50-100 m, so its child zigzagged at that scale.
  - Fix, in `zoom_fine._courses`: each parent course (main stem: head to its confluence, lip or sea) is smoothed by 1 parent px. It gets a gentle planet-fixed wander (0.15 parent px at ~4 px), and its planform is chosen per reach:
    - Alluvial: slope under 0.6% x rock erodibility.
    - Single-thread: under 1.5-3x the Leopold-Wolman 0.013 Q^-0.44. These reaches get a sine-generated meander train, wavelength 11 w, swing up to 1.2 rad (bend radius ~2.2 w).
    - The swing is limited by the valley floor's half width and the valley's own bends.
    - Meanders are drawn only where this zoom resolves them (15-24 px) and a fine parent didn't. The phase runs down the parent's whole network, so siblings agree.
  - Bedrock/steep and braided reaches keep the smoothed course. Tributaries end on their main river's course.
  - The river inflow check (water that already passed through the built area) is now by discharge, not a yes/no. With the wider parent box the old check dropped a 25 m^3/s river into 3e74b0 / b3c260 (relates PW-391).
  - New `zoom_fine.planform` metric, also in stats `river_planform`. It counts switchbacks (turns over 75 degrees across chords of max(3 px, 1.5 w)) and gives sinuosity on steep and gentle reaches, plus the course classes in km.
  - Test: `test_river_planform[bedrock|alluvial]`. The old code fails it with 9 and 7 switchbacks and a bedrock sinuosity of 1.22.
  - Showcase numbers, q >= 10, before -> after, switchbacks/km: b3c260 2.42 -> 0, 3e74b0 1.19 -> 0. Steep sinuosity: b3c260 1.29 -> 1.02.
  - Follow-ups (drafts): floodplains in the fine pass (lowland rivers in V valleys count as confined), braided threads, small D8 streams.
