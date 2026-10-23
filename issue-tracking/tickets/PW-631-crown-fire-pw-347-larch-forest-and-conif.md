---
id: PW-631
title: "Crown fire (PW-347): larch forest and conifer fuel build-up left out; forest cover >= 60% down 2.5 Mkm2"
type: task
status: todo
parent: PW-184
milestone: v2
subsystem: surface
effort: s
impact: low
found_by: soilveg2
blocked_by: []
relates: [PW-347, PW-234]
refs: [planet/vegetation.py, tools/veg_check.py]
created: 2026-10-23
updated: 2026-10-23
---

## Description
PW-347 added a crown-fire burned share for evergreen needleleaf stands (`vegetation.CROWN_FIRE` 0.08 x fire season x their cover x ignition, on top of GlobFIRM's grass-curing curve). Earth, observed climate: boreal rotation 294 -> 218 yr (GFED 166-216), median cell interval 382 -> 286 yr; savanna 3.82 -> 3.80 and grassland 1.32 -> 1.32 Mkm2/yr; potential-vegetation agreement 62.1 -> 62.0%. Left out:
- larch (BoNS, East Siberia) gets no crown term (deciduous needles; its fires are surface fires in the moss and litter), so Yakutia's frequent fires come only from the grass-curing curve;
- the conifers' fuel is the yearly litter: no build-up of ladder fuels and moss after a fire (the shrubs' slow pool would do it, `SLOW_FUEL`);
- forest with >= 60% trees falls from 46.2 to 43.7 Mkm2 (potential vegetation ~55-60): fire opens the boreal canopy, which is right for the taiga mosaic but widens an existing shortfall.
- A dry-spell term (rain days at random, (1 - f)^4) was tried first and dropped: boreal months already count 30-50% dry from their rain/evaporation ratio, so it moved boreal fire only 294 -> 240 yr while adding temperate burning (30-45 N +15-30%).

## Updates
- 2026-10-23: Created from inbox draft draft-veg-crown-fire-followups.md (found by soilveg2).
