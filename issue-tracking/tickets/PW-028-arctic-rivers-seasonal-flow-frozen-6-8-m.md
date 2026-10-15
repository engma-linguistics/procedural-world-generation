---
id: PW-028
title: "Arctic rivers: seasonal flow (frozen 6-8 months, spring flood)"
type: task
status: todo
parent: null
subsystem: hydrology
effort: m
impact: med
found_by: daniel
blocked_by: []
relates: []
refs: [planet/hydrology.py, planet/climate.py, "zoom f81832", "world 0f7abd", planet/world.py, planet/coast.py, planet/zoom.py, viewer/index.html]
created: 2026-10-14
updated: 2026-10-15
---

## Description
Rivers in cold climates should carry most of their water in a spring flood after 6–8 frozen months,
not a steady annual mean. That changes delta form (ice-dammed floods, river-dominated) and the zoom's
river look. Model it as a seasonal discharge profile from the monthly temperature (snow storage,
melt), at least as a stored "flood ratio" per cell for the zoom and deltas. Reference: zoom f81832 on
world 0f7abd (Lena-like: 2.2 Mkm², −12 °C mean, 16,800 m³/s).

## Updates
- 2026-10-15: Hydro (merged): flood_ratio/flood_month layers exist; consumers (deltas, zoom, viewer) remain.
- 2026-10-15: Merged inbox draft draft-flood-ratio-consumers.md ("Use the rivers' seasonal flood (flood_ratio, flood_month) in deltas, the zoom and the viewer", found by hydro).
  PW-028's data side is in: worlds store `flood_ratio` (peak month's flow / mean month's,
  hydrology.seasonal_flow) and `flood_month` (1-12). On the Earth world: Amazon 1.3, Congo 1.6,
  Mississippi 1.7, Ob 3.3, Mackenzie 3.1, Yukon 4.3, Volga 3.9, Ganges 3.9 (observed roughly 1.4, 1.3,
  1.7, 2.3, 2.5, 3, 4, 5). Nothing uses them yet:
  - [ ] coast.py delta type: a spring-flood river (ratio >= ~3, frozen sea in winter) delivers its sediment
        in a pulse, pushing the delta toward river-dominated (reference zoom f81832 on world 0f7abd).
  - [ ] zoom: river width / braiding and bank-full channels from the flood ratio (wide gravel braids on
        Arctic and monsoon rivers, steady single channels on lake-fed ones).
  - [ ] viewer: a layer for flood_ratio (and the peak month) in the cell inspector / layer list.
  Known gaps of the profile: no travel time down big rivers (a month-scale lag), no glacier melt,
  temperate rain-fed rivers are a bit too peaky (Danube 2.9 vs ~1.6; BASEFLOW 0.5).
- 2026-10-14: Note from PW-027 (quickwins): the reference mouth of zoom f81832 (51.6 N, -13.3 on world 0f7abd) is on an ice-free sea (sea cells' cold month +2 to +3.5 C; wave power 26-67 kW/m), so sea-ice damping leaves its delta wave-dominated. Only the cold basin is Arctic; a spring-flood sediment pulse (this ticket) is what could push it toward river-dominated.
- 2026-10-14: Created from the owner discussion 2026-10-14.
