---
id: PW-063
title: Test the zoom with real lake_level / lake_kind / runoff layers
type: task
status: todo
parent: null
subsystem: zoom
effort: s
impact: low
found_by: zoomwater
blocked_by: []
relates: []
refs: [planet/zoom.py, tests/test_zoom_water.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
The zoom's lake and river code was only exercised on the fallback path (worlds without `water`'s layers).
Add a test (`tests/test_zoom_water.py`) on a world that has `lake_level`, `lake_kind` and `runoff`,
including a closed lake.

## Updates
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Rivers, lakes, sediment (zoom lakes).
