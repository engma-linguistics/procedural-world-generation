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
refs: [planet/vegetation.py, tools/veg_check.py]
created: 2026-10-16
updated: 2026-10-16
---

## Description
Left from PW-234 (its "fire-weather month for boreal summers"). On Earth (observed climate, batch 2026-10-16) the boreal named types burn 0.06 Mkm2/yr, median fire return ~380 yr (25th-75th percentile 215-740); GFED4s boreal (BONA + BOAS) is ~0.1 Mkm2/yr and fire returns in the boreal forest are ~50-200 yr. Fuel is not the limit there (fine fuel 400-760 g C/m2, above FUEL_MIN + FUEL_SPAN); the fire season is: boreal summer months with rain at 50-70% of the potential evaporation already count as partly dry (site(): (1 - ratio) / 0.8 of a month), giving 1-2 dry months (season 0.08-0.16), where globfirm's logistic (tuned so a 5-month savanna burns ~1/3 a year) gives only ~1/150 to ~1/60 a year, times an ignition of ~0.5.
What to try: dry spells inside wet months (boreal fire weeks), e.g. the fire season's share from the month-to-month rain variability rather than the mean ratio; or a crown-fire term for conifer stands whose fuel builds up (as the shrubs' since PW-234) with their own weather threshold. Check that the savanna/forest boundary and the burned share in grassy types (79%, GFED ~70-80%) stay put.
- [ ] boreal fire return ~50-200 yr on Earth's observed climate, savanna and grassland numbers unchanged

## Updates
- 2026-10-16: Created from inbox draft draft-veg-boreal-fire-weather.md (found by vegbatch).
