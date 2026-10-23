---
id: PW-673
title: Peoples' land use in a zoom leaves soils, fire and the named types as they were
type: task
status: todo
parent: PW-103
milestone: v2
subsystem: zoom
effort: m
impact: low
found_by: zoompeoples
blocked_by: []
relates: [PW-667, PW-661]
refs: [planet/zoom_peoples.py, planet/zoom_vegetation.py, planet/soils.py, planet/vegetation.py]
created: 2026-10-23
updated: 2026-10-23
---

## Description
PW-667's overlay changes the plant fractions, tree cover, plant cover, leaf area, npp, canopy height, fire return, the named vegetation type (cleared woods become the open type of their climate: tropical grassland, steppe or prairie, parkland) and the biome. Left as they were: the soil layers (`soil_carbon`, `soil_fertility`, `peat_depth`: fields lose carbon over centuries, drained peat shrinks, grazed land compacts), the game layers' reading of `land_use` (gameattrs `grazing`/`foraging`/`timber`/`fuel` are re-derived from the new plants but know nothing of fields or villages), and the human-use `fertile` score (a field is shown on farmland as it was). And the vegetation legend has no 'cropland' or 'pasture' type: fields show as grassland types, with `land_use` saying what they are.

What to try: a `land_use` input to soils.organic (carbon x 0.6 under fields, x 0.85 under pasture, none on villages), to gameattrs (fields give no timber and little foraging; managed woods more fuel), and decide (needs the owner) whether the named vegetation types should grow 'cropland' and 'pasture' entries (the legend and goldens would change).
- [ ] soil carbon under the demo zoom's fields is lower than under its neighbouring wild ground

## Updates
- 2026-10-23: Created from inbox draft draft-zoom-peoples-soils-and-names.md (found by zoompeoples).
