---
id: PW-1302
title: Land zoom rivers and lakes continuous across sections
type: task
status: todo
parent: PW-1299
milestone: v2
subsystem: zoom
effort: l
impact: high
found_by: owner
blocked_by: [PW-1300]
relates: []
refs: [planet/hydrology.py, "planet/zoom/regional.py::zoom", planet/zoom/match.py, "planet/zoom/stage_rivers.py::coarse_rivers", docs/review/land-zoom/seams-round2.md, docs/review/land-zoom/seams.py]
created: 2026-11-02
updated: 2026-11-02
---

## Description
**In plain words.** A river crossing three sections must be one river: same course, flow and lakes. Options: one planet-wide drainage pass at zoom resolution, or each section conditioned on the world's routing with fixed inflow/outflow points on its edges. Judged on the practice sections.

## Updates
- 2026-11-02: Notes from lane 127 (folded from PW-1344): matched sections end their rivers at the owner line (held ground is an outlet via match.hold_edge), discharge not handed on; neighbour's crossing rivers could enter as inflows (ctx.inflow_pts, stage_rivers.coarse_rivers) with courses pinned in the held zone; multi-crossing rivers need a second pass or planet-wide coarse discharge routing both sides read; measure with seams.py river columns at the owner line (cell edge for tiling sections).
- 2026-11-02: Created.
