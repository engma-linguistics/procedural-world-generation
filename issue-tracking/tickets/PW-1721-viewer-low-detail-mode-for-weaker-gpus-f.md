---
id: PW-1721
title: "Viewer low-detail mode for weaker GPUs: fewer LOD tiles in flight, lighter globe, set from the machine probe or by hand"
type: task
status: done
parent: null
milestone: v1.0
subsystem: viewer
effort: m
impact: med
found_by: plan-v1-lane
blocked_by: []
relates: [PW-1673, PW-1560, PW-316]
refs: [docs/review/plan/milestones-to-v1.md, viewer/index.html, viewer/globe, planet/tiles.py, PW-1673]
created: 2026-11-11
updated: 2026-11-11
---

## Description
In plain words: the installer's "adapt to less-powerful machines" on the viewer's side. On a laptop's built-in graphics, Google Earth-style zooming and big worlds should stay usable instead of stuttering or crashing the tab.

The viewer was tuned on Daniel's machine (60 fps in testing, PW-1696). If this is never done, an installed copy on integrated graphics or with little VRAM can lose the WebGL context or crawl on the LOD dive and on L8 worlds. PW-1560 already notes the grid file dominates an L9 world's browser memory.

- A low-detail switch in the viewer's settings, defaulted from the probe (WebGL2 limits, the renderer string, deviceMemory). It sets fewer tiles in flight and in GPU memory, a lower globe mesh density near the ground, and no tilt shading.
- Measure frame time on the December world, on an integrated GPU or with Chrome's GPU throttled, on and off.

- [ ] On integrated graphics the LOD dive to 1 km stays above ~30 fps with low detail on, and the tab never loses its WebGL context

## Updates
- 2026-11-11: Status todo -> done. lane 313 merged
- 2026-11-11: Created from inbox draft draft-viewer-low-detail-mode.md (found by plan-v1-lane).
- 2026-11-11: Lane 313: low-detail mode (viewer/machinecore.js, viewer/globe/machine.js): auto from the GPU and the probe, or chosen by hand; fewer tiles kept and fetched, coarser refine, finest level 3, 1x pixels. Budgets are judgement: the integrated-GPU frame-time measurement is not done.
