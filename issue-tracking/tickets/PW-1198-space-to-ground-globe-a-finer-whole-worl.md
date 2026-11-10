---
id: PW-1198
title: "Space-to-ground globe: a finer whole world (L8/L9 finish) and a level-of-detail globe that zooms from orbit to the ground"
type: epic
status: todo
parent: null
milestone: v1.0
subsystem: viewer
effort: xl
impact: high
found_by: coordinator
blocked_by: []
relates: [PW-490, PW-1008, PW-1143, PW-316, PW-516, PW-253]
refs: [docs/review/l8-world/]
created: 2026-10-31
updated: 2026-11-10
---

## Description
**In plain words.** The owner (2026-10-31) wants the "zoom in from space down to the ground" view other world generators have, and a sharper whole world. Stay in the browser (three.js; WebGPU later), no engine switch: the limit is drawing every cell at full detail, not the engine.

Layers, coarse to fine: the simulated L7 globe (always drawn); a whole-world finish refined to L8/L9 (PW-490) for the finished moment; regional and fine zooms (1-4 km down to 25-250 m) where they exist; cosmetic GPU detail below that which keeps every parent cell's mean (PW-1008), never fed back into the physics.

v2 (right after the v1.0 tag, owner: "at least a try at some of it fairly immediately"): one lane, with half the CPUs and the GPU (RTX PRO 6000, 96 GB) if it helps.
- [ ] PW-490 first cut: refine a finished L7 world to L8 (terrain from the zooms' landform synthesis keeping parent means; rivers/lakes/coasts recomputed; climate downscaled; soils/vegetation/biomes per cell), measured cost; compare with lane 86's native L8 world.
- [ ] Chunked level-of-detail globe: coarse globe always, finer patches loaded for visible tiles near the camera (builds on PW-316's data textures).
- [ ] A first continuous zoom from the globe into an existing regional zoom without a page change.
v3: the real GPU work (detail synthesis in shaders, seamless streaming down to fine-zoom scale, L9 everywhere).

## Updates
- 2026-11-10: Owner 11-10: required for v1.0 (milestone v1.0): from the globe, zoom into a ~4,000 km section, then down to the finest zooms we have.
- 2026-11-03: Triage 11-03: v2 -> later: L8/L9 whole-world work, post-v2 (see PW-1198 space-to-ground globe)
- 2026-11-01: Lane 104 merged: planet refine (L7 -> L8/L9). World fb5e11 (from L7 783674, run b13ee9). L8 route ~20-25 min vs 146 direct; L9 38 min / 38.8 GB, too big for the viewer (PW-1209). docs/review/refine-l8/report.md
- 2026-10-31: Owner 10-31 asked for the L7-then-L8/L9 refine overnight: lane 104.
- 2026-10-31: Created from inbox draft draft-space-to-ground-globe-epic.md (found by coordinator).
