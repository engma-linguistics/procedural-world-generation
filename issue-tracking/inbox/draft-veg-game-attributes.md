---
title: "Vegetation game attributes, satellite colours and export fields (PW-187 step 9)"
type: task
status: todo
parent: PW-184
subsystem: viewer
effort: m
impact: med
found_by: veg
blocked_by: []
relates: [PW-187, PW-083, PW-100]
refs: [planet/vegetation.py, viewer/index.html, docs/proposals/vegetation.md]
---

## Description
Step 9 of the vegetation proposal (section 8.2, decision 11A: computed continuously from layers, the per-type table as fallback text). The named types already carry a game-facing line (`vegetation.TYPES`, legend `vegetation.types[].text`; the viewer shows it as the legend tooltip). Still to do: travel cost, visibility, forage, timber, fuel, water, fire season, hazards and seasonal look from tree_cover, canopy_height, stand_age, lai_jul/jan, npp, flooded, fire_return; a hover-card line; the satellite view (PW-083: colour = sum of PFT cover x PFT colour x seasonal LAI greenness + bare soil and snow; lai_jul/jan exist); export fields for PW-100.
