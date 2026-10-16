---
id: PW-185
title: "Soils: type and fertility per cell and per zoom pixel from rock, climate, slope, age, ice and loess"
type: story
status: in-progress
parent: PW-184
subsystem: surface
effort: m
impact: high
found_by: daniel
blocked_by: []
relates: [PW-095]
refs: [tools/earth_data.py, planet/surface.py]
created: 2026-10-14
updated: 2026-10-15
---

## Description
Owner must-have. Soil order/type (e.g. a WRB/USDA-like set of ~12-20: leached tropical oxisols, black-earth mollisols, podzols, thin glacial leptosols, aridisols with caliche/salt, volcanic andosols, floodplain fluvisols, peat histosols, permafrost cryosols, loess-derived) and fertility/depth from parent rock (strata_top), climate (warmth, water balance), slope, surface age since last disturbance (exhumation, glaciation_myr, rift/fold age), deposition (floodplains, deltas, loess downwind of ice margins and deserts). World layers plus zoom pixels (inheriting from the zoom's own slope, rivers, ice). Viewer layer and hover. Earth check against a soil map (e.g. HWSD/SoilGrids major groups) as an analogue. World-level only: no run cost.

## Updates
- 2026-10-15: Status todo -> in-progress. Agent started: proposal steps 1-5 and 8 (world soils, loess, vegetation hand-off, Earth check, viewer, climate memory). Steps 6 (zoom), 7 (run coal, serial run lane), 9 later.
- 2026-10-15: Status needs-decision -> todo. Owner 2026-10-15: approved all 7 leans of docs/proposals/soils.md (1A 2A 3B 4C 5A 6A 7A).
- 2026-10-15: Merged inbox draft draft-glim-rock-mapping.md ("GLiM-to-ROCKS mapping for soils' parent rock is a judgement call", found by soildata).
  `earth_glim` maps the 16 GLiM first-level classes onto `surface.ROCKS` ids (`GLIM_TO_ROCK` in tools/earth_data.py) for the soils check. ROCKS has no gabbro, rhyolite or diorite, so some rows are approximations: basic plutonics -> hotspot basalt, intermediate plutonics and volcanics -> arc, acid volcanics and pyroclastics -> tuff, unconsolidated sediments -> `sediment`, mixed sediments -> shale. Result at L6: sediment 29%, sandstone 18%, shale 16%, metamorphic belt 16%, limestone 8%, granite 6%, flood basalt 4%; no craton, dolomite or quartzite (GLiM cannot tell them apart; shields show as metamorphic or granite).
  Options: (A) keep as is, the soils' rules key on carbonate / basic / acid / sand / clay / loess-prone parent material and these rows separate those; (B) add a coarse `parent material` class set for soils (carbonate, basic, acid, siliciclastic, clay, unconsolidated, volcanic ash) and map both GLiM and the model's rocks onto it; (C) map metamorphics and granites on old shields to craton using the model's own age. Lean: A until the soil rules are written (PW-185), then B if they need it.
- 2026-10-15: Status in-progress -> needs-decision. Proposal ready for owner review: docs/proposals/soils.md, 7 numbered decisions (§ decisions) with leans.
- 2026-10-15: Proposal for owner review: docs/proposals/soils.md (19 types, two passes around vegetation, coal from peat, SoilGrids Earth check; 7 decisions in section 9.2).
- 2026-10-15: Status todo -> in-progress. Soils proposal for owner review being written (docs/proposals/soils.md), covering PW-212's interface.
- 2026-10-14: Absorbs PW-095: include permafrost, wetlands and peat.
- 2026-10-14: Created.
