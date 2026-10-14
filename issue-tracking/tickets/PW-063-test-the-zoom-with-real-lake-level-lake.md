---
id: PW-063
title: Test the zoom with real lake_level / lake_kind / runoff layers
type: task
status: done
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
- 2026-10-14: Status todo -> done. zoomsmalls: tests/test_zoom_water.py has a closed-lake world (lake_level/lake_kind/runoff from hydrology.rivers_and_lakes, level 80 m below spill) and checks every open fragment has an outlet; the existing open-lake world already used the real layers.
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Rivers, lakes, sediment (zoom lakes).
