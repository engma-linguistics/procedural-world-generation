---
title: Regional zooms draw a below-sea-level depression flat at 1 m (its lake keeps its depth)
type: task
status: todo
parent: null
milestone: v2
subsystem: zoom
effort: m
impact: low
found_by: lane98
blocked_by: []
relates: [PW-1229, PW-356]
refs: [planet/zoom/regional.py, planet/zoom/stage_finish.py]
---

## Description
In plain words: since PW-1229 a world's ground below sea level that is cut off from the ocean is land (the Dead
Sea, Qattara, Death Valley kind). The regional zoom's passes take land as ground above 0 m, so `zoom.land_world`
(planet/zoom/regional.py) raises such a cell's bed to 1 m for them, as it does for a bed under grounded ice, and a
lake on it keeps its depth on that floor. So a zoom shows a dry depression as a flat 1 m plain and its true depth
only in the stats (`e_bed`, `coarse_mean_elev_m`). The ice case already sinks the bed back after the passes
(stage_finish.ice_bed, PW-356); a depression could be sunk back the same way once the rivers and lakes are laid
out, with the zoom's own sea mask kept from the land view (so the fine pixels below 0 in it stay land).
- [ ] a zoom over a dry depression 100+ m below the sea shows its floor below 0 m and no sea in it
