---
id: PW-347
title: "Vegetation fire: boreal forest burns every ~380 yr (observed ~50-200); short fire seasons get little from GlobFIRM's curve"
type: task
status: todo
parent: null
subsystem: surface
effort: s
impact: low
found_by: vegbatch
blocked_by: []
relates: [PW-234, PW-205]
refs: [planet/vegetation.py, tools/veg_check.py, tools/earth_data.py]
created: 2026-10-16
updated: 2026-10-16
---

## Description
Left from PW-234 (its "fire-weather month for boreal summers"). On Earth (observed climate, batch 2026-10-16) the boreal named types burn 0.06 Mkm2/yr, median fire return ~380 yr (25th-75th percentile 215-740); GFED4s boreal (BONA + BOAS) is ~0.1 Mkm2/yr and fire returns in the boreal forest are ~50-200 yr. Fuel is not the limit there (fine fuel 400-760 g C/m2, above FUEL_MIN + FUEL_SPAN); the fire season is: boreal summer months with rain at 50-70% of the potential evaporation already count as partly dry (site(): (1 - ratio) / 0.8 of a month), giving 1-2 dry months (season 0.08-0.16), where globfirm's logistic (tuned so a 5-month savanna burns ~1/3 a year) gives only ~1/150 to ~1/60 a year, times an ignition of ~0.5.
What to try: dry spells inside wet months (boreal fire weeks), e.g. the fire season's share from the month-to-month rain variability rather than the mean ratio; or a crown-fire term for conifer stands whose fuel builds up (as the shrubs' since PW-234) with their own weather threshold. Check that the savanna/forest boundary and the burned share in grassy types (79%, GFED ~70-80%) stay put.
- [ ] boreal fire return ~50-200 yr on Earth's observed climate, savanna and grassland numbers unchanged

## Updates
- 2026-10-16: Merged inbox draft draft-veg-boreal-fire-gfed-rotation.md ("Boreal fire return: GFED4.1s gives a ~170-220 yr rotation on Earth's boreal forest, not 50-200 (update for PW-347)", found by pw204-vegdata).
  For the coordinator to merge into PW-347 (`board.py intake --merge-into PW-347`). veg_check now measures boreal fire on gridded GFED4.1s burned area (2001-2015 mean, small fires included). L6 Earth world 7873f9 (deleted), observed climate, fire rotation (area / area burned a year) and median cell interval:
  - model's boreal types: rotation 294 yr, median 381 yr, 0.058 Mkm2/yr;
  - GFED on the same cells: rotation 166 yr, median 510 yr;
  - GFED on potential vegetation's boreal forest (Ramankutty & Foley classes 6-7): rotation 216 yr, median 561 yr, 0.04 Mkm2/yr.
  So the observed target for PW-347 is a rotation of ~170-220 yr at this resolution (15 years of satellite data; fire concentrates in a few cells, which is why the median is longer than the rotation), and the model is ~1.4-1.8x too long, not 2-7x. PW-347's "50-200 yr" comes from stand-scale literature. Suggest changing its acceptance to "boreal rotation 150-250 yr (GFED 166-216)".
- 2026-10-16: Created from inbox draft draft-veg-boreal-fire-weather.md (found by vegbatch).
