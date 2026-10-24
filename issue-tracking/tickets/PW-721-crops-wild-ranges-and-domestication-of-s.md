---
id: PW-721
title: "Crops: wild ranges and domestication of staple plants (grain grasses, rice, maize-like, millet/sorghum, tubers, pulses), homelands, spread and effects on farming"
type: story
status: todo
parent: PW-691
milestone: v2
subsystem: timezoom
effort: m
impact: high
found_by: coordinator
blocked_by: []
relates: []
refs: []
created: 2026-10-23
updated: 2026-10-23
---

## Description
Plants half of PW-691, in the same Animal-table shape: each crop a row with a wild range from climate and soils (temperature, rain, season length, wetland for rice), an anchor date, who domesticates it (farmers and foragers on the range), a spread front and carry rule (seed travels easily, by boat too), and an effect (farm capacity, which land use counts as cropland). Several homelands per world, as on Earth (Fertile Crescent, China, Mesoamerica, Andes, Sahel, New Guinea). Store per cell the crops known; the culinary pass (PW-692) reads them. Fantasy rows rare, gated by world mode.

## Updates
- 2026-10-24: Built on branch fun7: crops as rows of the animals' table shape (planet/lineages/crop_defs.py, crops.py; ten real staples with real-world analogues, two rare fantasy rows mode-gated), wild ranges from climate and soils, several homelands per world, uint16 bit-flag layers crop_wild / crop_known (known and growable), farm capacity and a cropland gate; see docs/proposals/lineages.md 'Crops (PW-721), hunters tame (PW-718), fuels (PW-722) and one craft ladder (PW-720)'. Fruit/oil/spice/sugar plants and the cropland floor are drafts.
- 2026-10-23: Created.
