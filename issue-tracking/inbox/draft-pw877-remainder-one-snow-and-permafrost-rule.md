---
title: "PW-877 remainder: months' snowmelt and the three permafrost tests still disagree"
type: task
status: todo
parent: null
milestone: null
subsystem: climate
effort: s
impact: low
found_by: v1-finish-17
blocked_by: []
relates: [PW-877]
refs: [planet/climate.py, planet/icemass.py, planet/soils.py, planet/vegetation.py, planet/hydrology.py]
---

## Description
v1-finish-17 did only PW-877's cleanup: the dead earth.degree_days is deleted and climate.SNOW_DDF's stale "as
earth.ICE_DDF" comment now points at icemass. Left open:
- [ ] months (climate.py) melt snow at the monthly mean (SNOW_DDF, -2..+2 C ramp) while icemass uses PDD with sd 5,
  DDF 3/8, 60% refreeze: give months icemass's PDD melt (one snow rule)
- [ ] one permafrost class (soils' nival-offset one) shared by vegetation.flooded (temp < -2) and hydrology (>= 6 months below -2 C)
- [ ] measure the snow-albedo change with fmtally over two re-rolled draw sets
