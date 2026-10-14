---
id: PW-137
title: "Viewer: show the overturning circulation (AMOC-style) and make gyres legible"
type: task
status: todo
parent: null
subsystem: viewer
effort: s
impact: med
found_by: daniel
blocked_by: []
relates: [PW-013]
refs: [planet/ocean.py, viewer/index.html]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Owner looked for AMOC-like circular ocean patterns and found only the surface-current arrows. The model has both: wind-driven gyres (climate.currents, Stommel) in the 'Ocean currents' overlay, and the thermohaline overturning (planet/ocean.py: salinity, winter density, sinking in polar seas, Stommel strength), but the overturning is not stored or drawn. Store sea-surface salinity, sinking sites/strength and overturning strength (Sv) in worlds (and keyframes if cheap); draw sinking sites as markers, the deep return flow as a dashed path or a schematic loop, and report the overturning strength in the info panel. Also check the currents overlay renders gyres as visible loops (arrow density/streamlines) on a few worlds.

## Updates
- 2026-10-14: Created.
