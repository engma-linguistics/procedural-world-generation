---
id: PW-060
title: Zoom sees only part of a big lake's catchment
type: task
status: in-progress
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
- 2026-10-16: Status todo -> in-progress. Zoom batch 6 agent started.
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Rivers, lakes, sediment (zoom lakes).
