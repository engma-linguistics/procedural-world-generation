---
title: "Finished worlds: grounded marine ice is stored as land with the bed floored at 1 m"
type: task
status: todo
parent: PW-090
subsystem: timezoom
effort: s
impact: low
found_by: finish
blocked_by: []
relates: [PW-091, PW-189]
refs: [planet/finish.py, tools/earth_data.py]
---

## Description
The world format has no "grounded ice on a bed below sea level": land is elevation > 0. So
finish.py floors the bed of such cells (marine ice sheets, and beds pressed below the sea by
thick ice) at 1 m and thins the ice to keep the surface, as tools/earth_data.py does for
Antarctica. The bed shown under those cells is wrong (zooms, rock, a "lake" under the ice can't
appear); the surface is right. meta.marine_ice_floored_cells counts them. A proper fix stores the bed as is and lets world/climate/hydrology treat
"ice-covered, bed below sea level" as land (ties to PW-189 glacial isostasy).
