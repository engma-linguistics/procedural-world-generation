---
id: PW-203
title: "Vegetation feedbacks on climate (PW-187 step 6): Budyko w and evap_cool, albedo nudge, then rain recycling"
type: story
status: in-progress
parent: PW-184
subsystem: climate
effort: m
impact: med
found_by: veg
blocked_by: []
relates: [PW-187]
refs: [planet/climate.py, planet/vegetation.py, planet/tectonics/earth.py, docs/proposals/vegetation.md]
created: 2026-10-15
updated: 2026-10-15
---

## Description
Step 6 of the vegetation proposal (section 4.1-4.2; owner decision 6B: all three, rain recycling last). What exists after steps 1-4: the run keeps `sim.veg_frac` (19 x n cover), `sim.veg_lai`, `sim.tree_cover`, `sim.npp` and `sim.veg` (ground cover) at every climate update; worlds have the same in their layers. Climate runs before the vegetation in both, so the feedbacks need either the previous update's vegetation (run: one 4 Myr lag, fine) or a second climate pass in worlds.
- Budyko w per cell = 2.0 + 1.0 x woody cover (+0.3 deep-rooted evergreen), renormalised to Earth's land mean ~2.6 (`climate.water_balance` takes a scalar `TUNE["budyko_w"]` today).
- `evap_cool` from the summer AET/PET instead of the summer-rain proxy in `_land_finish`.
- Albedo nudge, capped +-2 C, snow under boreal conifers (Bonan 1992); tune so Earth's temperatures don't move on average.
- Rain recycling: `TUNE["et"]` (0.5) becomes a per-cell array from vegetation, clipped to a band around 0.5; watch for a forest-rain runaway.
Re-run tools/earth_check.py, tools/veg_check.py and the scorecard after each.

## Updates
- 2026-10-15: Status todo -> in-progress. Overnight agent, worktree vegclim.
- 2026-10-15: Created from inbox draft draft-veg-climate-feedbacks.md (found by veg).
