---
id: PW-099
title: "Human-use layers: navigable rivers, harbours, passes, fertile land, fresh water"
type: story
status: todo
parent: PW-090
milestone: v1
subsystem: surface
effort: m
impact: med
found_by: daniel
blocked_by: []
relates: [PW-095]
refs: [planet/world.py, planet/highlights.py]
created: 2026-10-14
updated: 2026-10-21
---

## Description
Derived layers for using a world: navigable rivers (discharge, gradient, no falls), natural harbours
(sheltered deep water near land), mountain passes (low saddles between basins), fertile land /
habitability (climate, soil, slope, water), fresh water availability.

## Updates
- 2026-10-21: Built (humanuse.py, branch agent-afb1254269fcb4287): river_nav, harbour, pass, fertile, fresh_water layers for worlds (world.finish) and zooms (zoom.build), export class maps + features (navigable_river, harbour, pass, spring, fertile_land), overview 2.22. Earth f6e955: Rhine/Mississippi/Yangtze navigable, estuary harbours yes, fjords no at L6 (zoom check pending), Alpine/Andean passes yes. Viewer not done (drafts: humanuse-viewer-layers, -fjord-harbours, -coarse-passes, -navigation-low-water-tides, -large-zoom-cost). Relates PW-475, PW-206.
- 2026-10-14: Created from the owner's world-finishing epic (2026-10-14).
