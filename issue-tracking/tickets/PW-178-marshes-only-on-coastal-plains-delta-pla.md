---
id: PW-178
title: Marshes only on coastal plains; delta plains, lagoon-less coasts and lake shores have none
type: task
status: todo
parent: null
subsystem: zoom
effort: s
impact: low
found_by: zoomland3
blocked_by: []
relates: [PW-012, PW-094, PW-061]
refs: [planet/zoom.py, "zoom:8373c5"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
PW-012 added a `wetland` layer (and an olive tint in the preview) for a
coastal plain's lowest wet ground near the sea and its lagoons (zoom
8373c5). Delta plains (tidal flats are drawn, but no salt marsh or swamp
behind them), the floodplains of big lowland rivers and the flat shores
of shallow lakes would get the same treatment; tidal marsh (mangrove in
the tropics) where the tide range is large. The biome layer has no
wetland class, so the viewer's legend shows them only in the hover info.

## Updates
- 2026-10-14: Created from inbox draft draft-marshes-beyond-coastal-plains.md (found by zoomland3).
