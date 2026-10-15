---
id: PW-205
title: "Vegetation on Earth: remaining misses (C4 crossover ~25 deg, boreal types 22 Mkm2, savanna in the southern Amazon fringe)"
type: task
status: todo
parent: null
subsystem: surface
effort: s
impact: low
found_by: veg
blocked_by: []
relates: [PW-187]
refs: [tools/veg_check.py, planet/vegetation.py]
created: 2026-10-15
updated: 2026-10-15
---

## Description
After tuning (observed climate, tools/veg_check.py --png): agreement 62%, land NPP 63 Pg C/yr, burned area 5.1 Mkm2/yr; all section-7 targets of the proposal within range except these smaller ones:
- The C4 share of grasses drops below half at ~25 deg (observed ~30-35, Still et al. 2003): C3 grasses win a little too far south; nudge the C4 temperature response or the C3 photorespiration penalty.
- Boreal named types cover ~22 Mkm2 (biome ~12-17, within the +-35% band but high): the boreal/temperate split in eastern Europe and NE China leans boreal (BoNE beats TeBS where potential vegetation has mixed forest).
- The southern Amazon fringe and much of the Brazilian shield are savanna where potential vegetation has forest (fire with a 3-4 month dry season; the forest state is stable there too, so it depends on the start).
- Burned area is 92% in savanna and grassland (GFED ~70-80%): boreal and temperate forest fires are rare (fire weather needs a dry month; boreal summers rarely qualify).

## Updates
- 2026-10-15: Smalls2: boreal 20.2->16.9 Mkm2 (in range); C4 nudges tried and rejected (draft).
- 2026-10-15: Created from inbox draft draft-veg-earth-tuning-remaining.md (found by veg).
