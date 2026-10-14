---
id: PW-100
title: "Export for game use: heightmap tiles, splat maps, feature GeoJSON"
type: story
status: todo
parent: PW-090
subsystem: store
effort: m
impact: high
found_by: daniel
blocked_by: []
relates: []
refs: [planet/zoom.py, planet/store.py, planet/images.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Export a world or zoom for game engines: heightmap tiles at a chosen resolution (16-bit), splat and
land-cover maps, and a feature list with coordinates (volcanoes, falls, lakes, resources, passes) as
JSON/GeoJSON. Some exists already: the zoom writes `heightmap.png` and `preview.png`.

## Updates
- 2026-10-14: Created from the owner's world-finishing epic (2026-10-14).
