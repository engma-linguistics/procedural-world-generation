---
id: PW-1296
title: "Whole-planet land zoom, the sweep: every land region at 4000 km sections, seamless, rivers continuous (last step of PW-1299)"
type: story
status: todo
parent: PW-1299
milestone: later
subsystem: zoom
effort: l
impact: high
found_by: owner
blocked_by: [PW-1300, PW-1301, PW-1302, PW-1303, PW-1338]
relates: [PW-1198, PW-541]
refs: [planet/zoom/regional.py::zoom, planet/zoom/stage_finish.py, planet/zoom/coastal.py, planet/zoom/fine.py, planet/parallel.py, "docs/coordination.md", docs/review/gpu/profile.md, "world 0af5ae", "world dba204"]
created: 2026-11-01
updated: 2026-11-03
---

## Description
**In plain words.** Daniel 11-01: rather than an L7 -> L9 refine, cover all of a world's land (not the ocean) with the regional zoom we already have (1-4 km/px). Compute is cheap: an L7 zoom of 1000 km at 2 km took 6.9 s per process (docs/coordination.md speed pass), and an Earth-like has ~170 Mkm2 of land, so ~200-250 overlapping 1000 km tiles is ~30 min one at a time, a few minutes in parallel at 2 km (roughly 4x that at 1 km); to be measured. The real work: (1) seams: neighbouring tiles must agree at their edges (heights, coasts, landforms; cf. PW-541's box-shaped cuts); (2) rivers and lakes routed across tiles so a river is one river (a planet-wide drainage pass at zoom resolution, or tiles conditioned on the world's routing); (3) storage and streaming: a tile pyramid the viewer loads by view, not one file; (4) cost and memory at 1 km. Order: after the v2 priority list (PW-252, PW-1295, PW-015/026, PW-1279, D34 B). First step: a written design and a timing of 10 adjacent tiles, with the seam problems measured.

## Updates
- 2026-11-03: Milestones 11-03: v2 -> later: owner 11-03: no whole-planet fine map is fine; the L7->L9 refine of the chosen world is v5
- 2026-11-02: Owner 2026-11-02: no whole planet at 1 km any time soon; the sweep targets 4 km/px. 1 km stays for single sections.
- 2026-11-02: Daniel 11-02: this is now the last step of epic PW-1299; the practice sections, seams, rivers and cost come first.
- 2026-11-01: Daniel 11-01: viewing folds into PW-1198's level-of-detail globe (orbit to ground). Start from the largest regional zoom, not 1000 km: regional.py allows up to 5000 km and 4096 px across, so 4000 km tiles at 1 km/px; ~15-20 tiles cover an Earth-like's land, with 4x less seam length per area than 1000 km tiles. Per-tile memory (16 M px x layers) is the thing to measure first.
- 2026-11-01: Created.
