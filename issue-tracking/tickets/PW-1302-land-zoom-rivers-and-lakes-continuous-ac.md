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
refs: [planet/hydrology.py, "planet/zoom/regional.py::zoom"]
created: 2026-11-02
updated: 2026-11-02
---

## Description
**In plain words.** A river crossing three sections must be one river: same course, flow and lakes. Options: one planet-wide drainage pass at zoom resolution, or each section conditioned on the world's routing with fixed inflow/outflow points on its edges. Judged on the practice sections.

## Updates
- 2026-11-02: Created.
