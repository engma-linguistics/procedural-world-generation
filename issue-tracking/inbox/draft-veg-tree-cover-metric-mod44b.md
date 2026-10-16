---
title: "veg_check tree cover: the model's tree share and MOD44B's canopy cover aren't the same quantity; no data north of 62.5 N"
type: task
status: needs-decision
parent: null
subsystem: infra
effort: s
impact: low
found_by: pw204-vegdata
blocked_by: []
relates: [PW-204]
refs: [tools/veg_check.py, tools/earth_data.py]
---

## Description
veg_check now compares tree cover with MOD44B C6.1 (UHH-ICDC 0.5 deg, 2001-2015 mean; PW-204). On L6 Earth world 7873f9, observed climate: the pattern matches (r by cell 0.71), the level doesn't: mean over land 0.35 vs 0.19, land with trees >= 60% 44.7 vs 7.7 Mkm2, forest-group mean 0.78 vs 0.35; 40-60 N bands 0.41-0.61 vs 0.17-0.29.
Reasons, not all model error: (1) MOD44B is today's land (cropland, pasture, logging: Europe, China, the eastern US) against the model's potential vegetation; (2) MOD44B is canopy cover of trees > 5 m and saturates near 80% in rainforest, while the model's `tree` is the tree PFTs' share of the ground; a 0.5 deg mean of a forest-savanna mosaic rarely reaches 60%; (3) the 0.5 deg product is 0% tree / 100% non-vegetated north of 62.5 N in every year (an artefact of that gridding), so the loader leaves it as no data and the northern taiga isn't compared at all.
Options: (A) keep as is, read the correlation and the zonal shape only (lean); (B) compare only where potential vegetation and today's land agree (mask cropland with a land-use map, e.g. HYDE or ESA CCI, more data); (C) also fetch a source for the north of 62.5 N (Hansen GFC treecover2000 tiles, ~GBs, or MOD44B from LP DAAC with the Earthdata login) to compare the taiga.
