---
id: PW-484
title: PROJ string for oblique Equal Earth / Mollweide / equirect export maps (ob_tran)
type: task
status: todo
parent: null
milestone: v1
subsystem: store
effort: xs
impact: low
found_by: pw477-export
blocked_by: []
relates: [PW-477, PW-100]
refs: [planet/projection.py, planet/export.py]
created: 2026-10-20
updated: 2026-10-20
---

## Description
`planet export --projection equirect|equal-earth|mollweide --center lat,lon` with a centre latitude other than 0 is an oblique map; `layouts.map.proj` is null there (only the rotation matrix `oblique_frame` is given), because pyproj is not in the env to verify an `+proj=ob_tran +o_proj=... +o_lat_p/+o_lon_p/+lon_0` string against our rotation (centre to 0N 0E, north up). Work out the ob_tran parameters, verify them against pyproj once (a throwaway env, not a dependency) at a few points, put them in `Projection.proj_string` and test the string's parameters.
- [ ] oblique proj string emitted and checked against pyproj for a few centres

## Updates
- 2026-10-20: Created from inbox draft draft-export-oblique-proj-string.md (found by pw477-export).
