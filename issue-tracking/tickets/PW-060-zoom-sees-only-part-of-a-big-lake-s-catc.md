---
id: PW-060
title: Zoom sees only part of a big lake's catchment
type: task
status: done
parent: null
subsystem: zoom
effort: m
impact: low
found_by: zoomwater
blocked_by: []
relates: []
refs: [planet/zoom.py]
created: 2026-10-14
updated: 2026-10-16
---

## Description
A zoom over a big lake passes on only the inflow it can see (45k of 125k m³/s in one case). Inject the
coarse world's full lake inflow at the outlet, as already done for rivers entering at the edge.

## Updates
- 2026-10-16: Status in-progress -> done. Done: a lake passes on at least the world's outflow (592f2a's biggest lake 0 -> 3,166 m3/s vs world 3,177); drops 9.8 -> 10.2 (a plateau lake's outflow now cascades).
- 2026-10-16: Zoom batch 6: fixed in b613824. A coarse lake's outlet (its fragment nearest the coarse exit) passes on at least the world's outflow of the lake, less what its other fragments pass on elsewhere; lakes routed upstream first along their outflows. 592f2a's 150,000 km2 lake in a 1000 km zoom: 0 -> 3,166 m3/s (world 3,177). Drops on the 8 zooms 9.8 -> 10.2 per seed (a 3,631 m plateau lake's doubled outflow cascades off the plateau). docs/review/zoom-polish/batch6.md.
- 2026-10-16: Status todo -> in-progress. Zoom batch 6 agent started.
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Rivers, lakes, sediment (zoom lakes).
