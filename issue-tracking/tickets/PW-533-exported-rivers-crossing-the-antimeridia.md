---
id: PW-533
title: Exported rivers crossing the antimeridian keep unwrapped longitudes past 180 (strict RFC 7946 importers need them split)
type: task
status: todo
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
- 2026-10-21: Created.
