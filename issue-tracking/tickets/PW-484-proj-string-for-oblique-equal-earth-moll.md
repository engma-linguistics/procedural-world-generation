---
id: PW-484
title: PROJ string for oblique Equal Earth / Mollweide / equirect export maps (ob_tran)
type: task
status: done
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
updated: 2026-10-21
---

## Description
`planet export --projection equirect|equal-earth|mollweide --center lat,lon` with a centre latitude other than 0 is an oblique map; `layouts.map.proj` is null there (only the rotation matrix `oblique_frame` is given), because pyproj is not in the env to verify an `+proj=ob_tran +o_proj=... +o_lat_p/+o_lon_p/+lon_0` string against our rotation (centre to 0N 0E, north up). Work out the ob_tran parameters, verify them against pyproj once (a throwaway env, not a dependency) at a few points, put them in `Projection.proj_string` and test the string's parameters.
- [ ] oblique proj string emitted and checked against pyproj for a few centres

## Updates
- 2026-10-21: Status todo -> done. Done: ob_tran strings for oblique equirect/equal-earth/mollweide: +o_lat_p=90-|lat0|, +o_lon_p=0 (north) or 180 (south, lon_0 shifted by 180), +lon_0=lon0. Verified against pyproj (throwaway uv --with, not a dependency) over 3 projections x 9 latitudes (-90..90) x 5 longitudes, 200 points each, forward and inverse: worst error 1.5e-7 m (limit 1 px = ~17 km at 2048 px wide). Parameters tested in tests/test_projection.py.
- 2026-10-20: Created from inbox draft draft-export-oblique-proj-string.md (found by pw477-export).
