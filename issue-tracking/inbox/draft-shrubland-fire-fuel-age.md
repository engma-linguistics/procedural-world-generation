---
title: "Vegetation fire: fuel has no age, so maquis and chaparral never burn (or turn to grass when they do)"
type: task
status: todo
parent: null
subsystem: surface
effort: m
impact: low
found_by: smalls2
blocked_by: []
relates: [PW-220, PW-205, PW-187]
refs: [planet/vegetation.py, tools/veg_check.py, "zoom:58c0ac", "world 351f32"]
---

## Description
PW-220's "maquis that never burns" and PW-205's "burned area 92-95% in savanna and grassland (GFED ~70-80%)" share one cause: `vegetation._step` takes the fuel as the equilibrium fine-litter stock (sum of nu x NPP x litf / decay rate) against FUEL_MIN = 250 g C/m2. Low-NPP sclerophyll scrub stays below the threshold (zoom 58c0ac maquis: NPP 230, no fire), and boreal forest rarely has a dry fire-weather month.

A plain nudge doesn't work (tried on branch smalls2): raising SclS `litf` 0.4 -> 0.8 lets maquis burn, but then it burns at a savanna's rate (GlobFIRM's season curve, ~1/3 of the land a year at 5 dry months) and the scrub turns to grass: Earth (observed climate) Mediterranean-type cells fell 68 -> 13 in the Mediterranean box, SW Australia 25 -> 13; burned area 5.1 -> 5.5 Mkm2/yr, still 92% in grassland.

Real shrubland and forest fires are fuel-age limited: chaparral and fynbos burn every 20-60 years because the dead fuel builds up over decades after a fire, crown fires need that build-up; savanna grass is ready every year. Proper fix: a fuel-age term, e.g. the burned share of woody types limited by 1 / (years to rebuild their fuel), fuel built from the woody types' standing dead (a share of their biomass) rather than only litter flux; and a fire-weather month for boreal summers (dry spells of a week are enough there).
- [ ] maquis / chaparral cells burn every ~20-60 yr and stay scrub (zoom 58c0ac, Earth Mediterranean boxes)
- [ ] veg_check: burned share in savanna and grassland nearer 70-80%, Mediterranean counts not lower
