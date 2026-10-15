---
title: "Vegetation types that look wrong in L7 zooms: heath on 200 mm plateaus, temperate forest at 3 S, maquis that never burns"
type: task
status: todo
parent: PW-184
subsystem: surface
effort: s
impact: med
found_by: vegzoom
blocked_by: []
relates: [PW-187, PW-207]
refs: [planet/vegetation.py, "world:351f32(-28.30,-16.50)", "world:351f32(-3.30,-70.83)", "zoom:58c0ac", "zoom:64f0b6"]
---

## Description
Zooming into world 351f32 (L7 vegetation demo) made some world-level classifications easy to see (the zoom reproduces them, they are the world model's):
- **Heathland and moorland on a dry high plateau**: world:351f32(-28.30,-16.50), ~2000 m, P ~190 mm/yr, mean 8.9 C: 42% of the land in the world's cells (and the zoom) is "heathland and moorland" (HthS-dominated shrubland). Heath is a wet, maritime type; at 200 mm this should be cold desert scrub or shrub steppe. classify() names shrubland by its dominant shrub only; HthS has amin 0.5 but wins on a cold dry plateau anyway. Check HthS's drought limit and add a moisture condition to the heath rule (mi > ~0.6).
- **"Temperate mixed forest" at 3 S, 800 m** (world:351f32(-3.30,-70.83), zoom 64f0b6 bottom right): coldest month ~17.5 C, P 2700-4500 mm. TeBS (tc_max 15.5) shouldn't be viable; TeNE + TeBE beat TrBE, or the dominant-tree rule picks the wrong family. Expect tropical (montane) rainforest there.
- **Mediterranean scrub with no fires** (zoom 58c0ac, hover at px 250,330: maquis, NPP 230, "no fires"): the fuel threshold (FUEL_MIN 250 g C/m2 of fine litter) keeps low-NPP maquis fire-free, though maquis, chaparral and fynbos are the fire-adapted types par excellence (fire every 10-40 yr). Perhaps SclS litter should be more flammable (litf) or the threshold lower for shrubland.
- **"Lichen woodland" on Mediterranean hills** (zoom 58c0ac, 29 N, ~1460 m, July 22 C, January 2 C, P 330 mm with a dry summer): 4% of the land, made of BoBS 22%, SclS 41%, TeBS 7% (zoom_vegetation.fractions). Birch (BoBS: tc_max 5 C, no lower limit, cheap and fast) takes the cooler hill pixels' sparse tree layer, and classify() names any woodland whose trees are mostly boreal "lichen woodland" (or forest-tundra). Shows more in zooms than in worlds because pixels reach higher; a Mediterranean upland should read as evergreen-oak or pine woodland. Perhaps BoBS needs a continentality or summer-moisture condition, and the boreal woodland names a boreal climate (tc < -2 C).
- [ ] each case checked against the world model and fixed or explained
