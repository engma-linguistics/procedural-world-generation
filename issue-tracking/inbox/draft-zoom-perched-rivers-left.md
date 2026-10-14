---
title: "Zoom: some river stretches still perched (under ice, beside other rivers)"
type: task
status: todo
parent: null
subsystem: zoom
effort: m
impact: low
found_by: zoomsmalls
blocked_by: []
relates: [PW-068]
refs: [planet/zoom.py, "zoom:1ef6c5", "zoom:3ea62e", "world:f724bd(54.0,-23.14)"]
---

## Description
PW-068 gave reaches with falls valley sides a few km wide (`banks()`): over 20 test zooms the river
pixels (>= 100 m3/s) with land within 2 px more than 30 m below them fell 702 -> 195 (> 100 m:
260 -> 11, worst 869 -> 364 m). What is left:
- under ice, where creep may lift a stream's bed (ICE_SNOUT_GRAD) and the land beside drains lower;
- where the banks skip another river (>= BANK_MAX_Q or another coarse river's valley bottom), so a
  lower parallel river runs within 2 px;
- the banks lift the land to the river rather than lowering the river: where a staircase sits far
  above the fine land, the result is a raised strip ~8 km wide with 30 m/km flanks. Fitting the
  staircase under the fine surface (e.g. the previous iteration's land around the course) instead
  of the coarse ground would lower the river with the land.
Metric: for river pixels >= 100 m3/s, min over land (< 30 m3/s) within 2 px vs the min river level
within 2 px of that land pixel.
