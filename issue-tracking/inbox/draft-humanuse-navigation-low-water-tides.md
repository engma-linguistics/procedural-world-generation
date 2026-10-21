---
title: River navigability uses the mean discharge: add low-water month and tidal reaches
type: task
status: todo
parent: PW-099
subsystem: hydrology
effort: s
impact: low
found_by: humanuse
blocked_by: []
relates: [PW-099, PW-028]
refs: [planet/humanuse.py, "world f6e955"]
---

## Description
`humanuse.river_nav` takes the depth from the mean discharge (0.27 Q^0.3 m) and the gradient over one world cell (about 8 km in a zoom), and closes a reach when frozen 9+ months. Two simplifications show on Earth: the Rhine comes out as barges all the way (sea-going ships reach Rotterdam on the tide and a deep dredged channel), and a monsoon or snowmelt river is rated on its mean although its low-water month may be too shallow (the world has `flood_ratio` and `flood_month`, PW-028; low water would scale the depth by roughly 1/flood_ratio). Tides push the sea-going limit upstream along a lowland river (the world has `tide_range`).
- [ ] low-water depth from the seasonal flow, as a second class (`river_nav_low`) or open months for each class
- [ ] sea-going up the tidal reach of a river whose mouth has a tide range above ~2 m and a gradient under 0.1 m/km
