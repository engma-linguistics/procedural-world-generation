---
title: Use the rivers' seasonal flood (flood_ratio, flood_month) in deltas, the zoom and the viewer
type: task
status: todo
parent: null
subsystem: coast
effort: s
impact: low
found_by: hydro
blocked_by: []
relates: [PW-028]
refs: [planet/hydrology.py, planet/world.py, planet/coast.py, planet/zoom.py, viewer/index.html]
---

## Description
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
