---
title: GLiM-to-ROCKS mapping for soils' parent rock is a judgement call
type: task
status: needs-decision
parent: null
subsystem: surface
effort: xs
impact: low
found_by: soildata
blocked_by: []
relates: [PW-314, PW-185, PW-132]
refs: [tools/earth_data.py, planet/surface.py]
---

## Description
`earth_glim` maps the 16 GLiM first-level classes onto `surface.ROCKS` ids (`GLIM_TO_ROCK` in tools/earth_data.py) for the soils check. ROCKS has no gabbro, rhyolite or diorite, so some rows are approximations: basic plutonics -> hotspot basalt, intermediate plutonics and volcanics -> arc, acid volcanics and pyroclastics -> tuff, unconsolidated sediments -> `sediment`, mixed sediments -> shale. Result at L6: sediment 29%, sandstone 18%, shale 16%, metamorphic belt 16%, limestone 8%, granite 6%, flood basalt 4%; no craton, dolomite or quartzite (GLiM cannot tell them apart; shields show as metamorphic or granite).
Options: (A) keep as is, the soils' rules key on carbonate / basic / acid / sand / clay / loess-prone parent material and these rows separate those; (B) add a coarse `parent material` class set for soils (carbonate, basic, acid, siliciclastic, clay, unconsolidated, volcanic ash) and map both GLiM and the model's rocks onto it; (C) map metamorphics and granites on old shields to craton using the model's own age. Lean: A until the soil rules are written (PW-185), then B if they need it.
