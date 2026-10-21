---
id: PW-476
title: "Game export: lakes as outlines and rivers with width or order"
type: task
status: todo
parent: null
milestone: v1
subsystem: store
effort: s
impact: low
found_by: export
blocked_by: []
relates: [PW-100]
refs: [planet/export.py]
created: 2026-10-20
updated: 2026-10-20
---

## Description
`planet export` (PW-100) writes each lake as one point (centroid, area, level) and each river as a
polyline with only its peak discharge. A game wants lake outlines (polygons: a zoom's `water == 2`
pixels traced, a world's lake cells merged) and rivers split with width / Strahler order or per-vertex
discharge, so a river can widen downstream and a lake can be a mesh. The lake pixels and `discharge`
are already there; this is tracing and a property. Also: rivers crossing the antimeridian keep longitudes
past 180 (unwrapped); split them into two lines if an importer needs strict RFC 7946.
- [ ] lake polygons in `features.geojson` and `features_local.geojson`
- [ ] per-vertex discharge or an order property on river lines

## Updates
- 2026-10-20: Created from inbox draft draft-export-lake-polygons-river-order.md (found by export).
