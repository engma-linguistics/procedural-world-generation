---
id: PW-062
title: "Zoom: small lake fragments with no outlet act as sinks"
type: task
status: done
parent: null
subsystem: zoom
effort: s
impact: low
found_by: zoomwater
blocked_by: []
relates: []
refs: [planet/zoom.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
A small lake fragment (cut by the zoom edge or the coarse mask) sometimes has no outlet and swallows its
river. Give every lake fragment an outlet (spill point) or merge it with land.

## Updates
- 2026-10-14: Status todo -> done. zoomsmalls: a closed lake's smaller fragments drain to its biggest one; an open fragment that finds no outlet becomes land. On 20 test zooms (28 lakes) no open fragment lacked an outlet; one closed-lake fragment (10 px, 12 m3/s, world:f724bd(14.45,-63.17)) now drains to the main lake.
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Rivers, lakes, sediment (zoom lakes).
