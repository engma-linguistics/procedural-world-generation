---
id: PW-100
title: "Export for game use: heightmap tiles, splat maps, feature GeoJSON"
type: story
status: done
parent: PW-090
subsystem: store
effort: m
impact: high
found_by: daniel
blocked_by: []
relates: []
refs: [planet/zoom.py, planet/store.py, planet/images.py]
created: 2026-10-14
updated: 2026-10-20
---

## Description
Export a world or zoom for game engines: heightmap tiles at a chosen resolution (16-bit), splat and
land-cover maps, and a feature list with coordinates (volcanoes, falls, lakes, resources, passes) as
JSON/GeoJSON. Some exists already: the zoom writes `heightmap.png` and `preview.png`.

## Updates
- 2026-10-20: Status todo -> done. Built: planet/export.py, `planet export <world|zoom>` (heightmap/ice 16-bit tiles, water/biome/vegetation/rock id maps, 8-material splat RGBA, features.geojson + zoom features_local.geojson, manifest.json, legend.json; cube faces for worlds). Tested on a synthetic L4 world and zoom (tests/test_export.py); documented in README. Follow-ups in inbox drafts; PW-099/PW-206 fields slot in as new layers and feature kinds.
- 2026-10-14: Created from the owner's world-finishing epic (2026-10-14).
