---
id: PW-1245
title: The weathering plants' CO2 starvation has no C4/CAM rescue, and the vegetation itself still holds CO2 at 124 ppm
type: task
status: todo
parent: null
milestone: later
subsystem: climate
effort: m
impact: low
found_by: lane95
blocked_by: []
relates: [PW-1227, PW-1224, PW-880]
refs: [planet/tectonics/earth.py, planet/vegetation.py, docs/review/v1-cut/plant-floor.md]
created: 2026-10-31
updated: 2026-11-03
---

## Description
In plain words. Lane 95 made the weathering sink's plants starve below 124 ppm of CO2 (PW-1227), using the C3 plants'
physiology on all of them. Two gaps remain. C4 grasses and CAM succulents starve far less at low CO2 (that is why
C4 grass spread at the Last Glacial Maximum), so treating all the planted ground as C3 makes the sink fall off a bit
too fast. And the vegetation that draws the biomes still holds its CO2 response at 124 ppm, so at 85 ppm the map shows
plants that the sink treats as starving.

- `earth._planted` scales the whole enhancement (PLANT_WEATHER - 1) by `vegetation.starvation` (C3 quantum yield ratio).
  Lane 94's offline estimate with 30% of the enhancement kept as C4/CAM: 65 ppm instead of 73 ppm in draw 639472, so
  this is a small correction (and the C4 group only arrives 35-25 Ma before the run's end).
- `npp_w` (PW-880) does not keep the PFT mix, so the C4 share is not available to the sink today.
- `vegetation.co2_doublings` clips at CO2_RANGE (124-990 ppm), so biomes and NPP never see the starvation.

Fix sketch: keep the C4/CAM share of `npp_w` (one more per-cell array) and exempt it from `starvation`; then lift the
124 ppm floor for the vegetation too, so biomes and sink agree. Test: unit test on the law, then the lane 95 screen
(docs/review/v1-cut/plant-floor.md) on the draws whose minima go under 124 ppm.
- [ ] C4/CAM share of the weathering plants kept and not starved
- [ ] vegetation's own CO2 response below 124 ppm (biome shifts checked on one low-CO2 frame)

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: calibration or second-order physics refinement, not needed for the planet to be stable or for the culinary goal
- 2026-10-31: Created from inbox draft draft-weathering-starvation-c4-and-biomes.md (found by lane95).
