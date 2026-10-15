---
title: "Vegetation to soils (PW-187 step 8): litter, waterlogging and peat to PW-185; coal from peat in the run"
type: task
status: todo
parent: PW-184
subsystem: surface
effort: s
impact: med
found_by: veg
blocked_by: []
relates: [PW-185, PW-187]
refs: [planet/vegetation.py, planet/tectonics/earth.py, docs/proposals/vegetation.md]
---

## Description
Step 8 of the vegetation proposal (section 4.4). Available now: per-PFT potential NPP and fine-litter share (`litf`; fuel uses it), the flooded share `fw` (world layer `flooded`), stand ages. PW-185 needs litter input (= NPP in equilibrium) and the waterlogging mask; it gives back the soil water capacity (vegetation uses fixed `TOP_MM`/`DEEP_MM` = 50/150 mm, thinned on steep cells) and a fertility factor (f_soil, not yet in the LUE formula). In the run, coal still uses `sim.veg > 0.5` (ground cover) in warm wet lowlands; replace it with peat accumulation (waterlogged NPP > slow decay). Also add the proposal's `litter_c` / `soil_c` world layers once PW-185 owns soil carbon.
