---
id: PW-234
title: "Vegetation fire: fuel has no age, so maquis and chaparral never burn (or turn to grass when they do)"
type: task
status: done
parent: null
milestone: null
subsystem: surface
effort: m
impact: low
found_by: smalls2
blocked_by: []
relates: [PW-220, PW-205, PW-187]
refs: [planet/vegetation.py, tools/veg_check.py, "zoom:58c0ac", "world 351f32"]
created: 2026-10-15
updated: 2026-10-16
---

## Description
PW-220's "maquis that never burns" and PW-205's "burned area 92-95% in savanna and grassland (GFED ~70-80%)" share one cause: `vegetation._step` takes the fuel as the equilibrium fine-litter stock (sum of nu x NPP x litf / decay rate) against FUEL_MIN = 250 g C/m2. Low-NPP sclerophyll scrub stays below the threshold (zoom 58c0ac maquis: NPP 230, no fire), and boreal forest rarely has a dry fire-weather month.

A plain nudge doesn't work (tried on branch smalls2): raising SclS `litf` 0.4 -> 0.8 lets maquis burn, but then it burns at a savanna's rate (GlobFIRM's season curve, ~1/3 of the land a year at 5 dry months) and the scrub turns to grass: Earth (observed climate) Mediterranean-type cells fell 68 -> 13 in the Mediterranean box, SW Australia 25 -> 13; burned area 5.1 -> 5.5 Mkm2/yr, still 92% in grassland.

Real shrubland and forest fires are fuel-age limited: chaparral and fynbos burn every 20-60 years because the dead fuel builds up over decades after a fire, crown fires need that build-up; savanna grass is ready every year. Proper fix: a fuel-age term, e.g. the burned share of woody types limited by 1 / (years to rebuild their fuel), fuel built from the woody types' standing dead (a share of their biomass) rather than only litter flux; and a fire-weather month for boreal summers (dry spells of a week are enough there).
- [ ] maquis / chaparral cells burn every ~20-60 yr and stay scrub (zoom 58c0ac, Earth Mediterranean boxes)
- [ ] veg_check: burned share in savanna and grassland nearer 70-80%, Mediterranean counts not lower

## Updates
- 2026-10-16: Status in-progress -> done. Done: shrub dead fuel decays at half the litter rate (Harmon 1986), burned patches rebuild fuel; SclS survival 0.9; SclS needs at most half its rain in summer (summer-drought adaptation). Earth Med types burn every ~28 yr. L7: thicket 549 -> 242, Mediterranean types 82 -> 133, tree cover 44.0 -> 33.5% (run keyframe 25%: monsoon cells keep the run's open state instead of regrowing forest from seed). Earth agreement obs 62.1% unchanged, model 41.6 -> 40.5%.
- 2026-10-16: Second follow-up: the humid exemption is removed (no physical basis); SclS needs at most half the rain in the warm half-year everywhere. The humid forest -> thicket was monsoon cells the run's keyframe had treeless (93%): an open start now stays open (fire), while a forest start stays forest (bistable, history decides). L7: thicket 549 (old) -> 242, Mediterranean types 82 -> 133, tree cover 44.0 -> 33.5% (keyframe 25.0%; the world follows its run's history twice as closely). Earth agreement 62.1 -> 62.1 obs, 41.6 -> 40.5 model. docs/review/vegetation/batch-2026-10-16.md
- 2026-10-16: Owner decision C on the shrub expansion: SclS needs a dry summer in dry climates (P/PET < 0.65: at most half the rain in the warm half-year); humid climates keep it. Earth obs (merged code): agreement 61.4 -> 61.5%, Med cells 96 -> 127, Botswana/Zambia grassland back, mallee belt on L7 1980 -> 656 cells. Humid forest -> thicket left as draft-veg-humid-thicket-fire-feedback.md. docs/review/vegetation/batch-2026-10-16.md
- 2026-10-16: Done on branch (vegetation batch 2026-10-16): shrubs' dead fuel decays at half the litter's rate and fire is a renewal process (fuel rebuild years + wait for a fire year); SclS fire survival 0.9. Earth obs: Mediterranean types burn every 28 yr (median; IQR 15-80), Med cells 97 -> 124, burned 79% in grassy types. Boreal fire weather left as draft-veg-boreal-fire-weather.md; shrub expansion as draft-veg-sclerophyll-expansion-after-fuel-age.md.
- 2026-10-16: Status todo -> in-progress. Vegetation batch agent started.
- 2026-10-15: Created from inbox draft draft-shrubland-fire-fuel-age.md (found by smalls2).
