---
id: PW-1302
title: Land zoom rivers and lakes continuous across sections
type: task
status: done
parent: PW-1299
milestone: v2
subsystem: zoom
effort: l
impact: high
found_by: owner
blocked_by: [PW-1300]
relates: []
refs: [planet/hydrology.py, "planet/zoom/regional.py::zoom", "planet/zoom/regional.py::zoom_id", planet/zoom/match.py, "planet/zoom/match.py::inflows", "planet/zoom/match.py::walls", "planet/zoom/match.py::basin_lakes", "planet/zoom/stage_rivers.py::coarse_rivers", "planet/zoom/stage_landscape.py::final_drainage", docs/review/land-zoom/seams-round2.md, docs/review/land-zoom/seams.py, docs/review/land-zoom/rivers.py, docs/review/land-zoom/rivers-round1.md, docs/review/land-zoom/rivers1/, tests/test_zoom_match.py, "zoom:5d2e02", "zoom:e2313a", "zoom:b9c5c8", "zoom:3580b7", "zoom:83b0b1", "zoom:a13667", "zoom:59336f", "zoom:0852e2", "zoom:d7b43d", "zoom:3b412b", "zoom:34d0a5", "world:dba204"]
created: 2026-11-02
updated: 2026-11-02
---

## Description
**In plain words.** A river crossing three sections must be one river: same course, flow and lakes. Options: one planet-wide drainage pass at zoom resolution, or each section conditioned on the world's routing with fixed inflow/outflow points on its edges. Judged on the practice sections.

## Updates
- 2026-11-02: Status todo -> done. Lane 129 (merged 8be2508b): A->B rivers carried on (48/53 crossings, 22/23 big within 25%; 1 km tile 20/21); walls + basin lakes; B->A needs a mosaic discharge pass after the sweep (follow-up). Notes docs/review/land-zoom/rivers-round1.md.
- 2026-11-02: Notes from lane 127 (folded from PW-1344): matched sections end their rivers at the owner line (held ground is an outlet via match.hold_edge), discharge not handed on; neighbour's crossing rivers could enter as inflows (ctx.inflow_pts, stage_rivers.coarse_rivers) with courses pinned in the held zone; multi-crossing rivers need a second pass or planet-wide coarse discharge routing both sides read; measure with seams.py river columns at the owner line (cell edge for tiling sections).
- 2026-11-02: Created.
