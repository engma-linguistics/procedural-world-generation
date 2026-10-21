---
id: PW-533
title: Exported rivers crossing the antimeridian keep unwrapped longitudes past 180 (strict RFC 7946 importers need them split)
type: task
status: done
parent: null
milestone: v1
subsystem: store
effort: xs
impact: low
found_by: pw476
blocked_by: []
relates: [PW-476]
refs: []
created: 2026-10-21
updated: 2026-10-21
---

## Description
planet/export.py river LineStrings that cross 180 E/W carry longitudes beyond +-180. Split them at the antimeridian into a MultiLineString per RFC 7946 section 3.1.9; same for lake polygons that straddle it.

## Updates
- 2026-10-21: Status todo -> done. Done: river LineStrings and lake polygons crossing the antimeridian are split at +-180 (RFC 7946 3.1.9; MultiLineString/MultiPolygon, crossing latitude interpolated, vertex_discharge_m3s a list per part). All longitudes now in [-180,180]. Tests added (synthetic crossing river and lake); world 577526 export checked clean (0 out-of-range positions, 4 multi-geometries, no misaligned discharge). README export notes updated. Full pytest passes.
- 2026-10-21: Created.
