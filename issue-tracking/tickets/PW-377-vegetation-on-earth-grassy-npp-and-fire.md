---
id: PW-377
title: "Vegetation on Earth: grassy NPP and fire too high in the northern subtropics, fire too low in the southern tropics (GFED4.1s, MOD17)"
type: task
status: todo
parent: null
subsystem: surface
effort: m
impact: med
found_by: pw204-vegdata
blocked_by: []
relates: [PW-347, PW-204, PW-013]
refs: [planet/vegetation.py, tools/veg_check.py, tools/earth_data.py]
created: 2026-10-16
updated: 2026-10-16
---

## Description
tools/veg_check.py now compares with gridded GFED4.1s burned area (2001-2015) and MOD17A3 NPP (2000-2015) (PW-204). On an L6 Earth world (7873f9, observed climate) the totals agree: burned 5.6 vs GFED 4.66 Mkm2/yr, NPP on common land cells 60.1 vs 54.8 Pg C/yr, rank correlation of burned fraction by cell 0.50, NPP r 0.49. The geography doesn't:
- burned area by 15-deg band (model / GFED Mkm2/yr): 15-30 N 0.72 / 0.14, 30-45 N 0.68 / 0.10, 45-30 S 0.29 / 0.04 (Patagonia), but 15 S-0 0.85 / 1.46 and 0-15 N 1.24 / 1.61. The model burns the Sahel's northern edge, the Middle East / central Asian steppes and Patagonia; GFED puts the fire in the southern African and Brazilian savannas.
- NPP of the grassy types is high: savanna 787 vs MOD17 484, grassland 395 vs 195 g C/m2/yr; the 10-20 N band 651 vs 339 and 20-30 N 572 vs 471 (Sahel and Sudan too productive, more fuel); tropical forest group 535 vs 639.
- the model's grassy share of fire is 91% against GFED's 78% on the same cells (63% on potential vegetation's savanna + grassland, 70% with shrubland; GFED includes crop and deforestation fires).
Part of it is the climate: on the model climate the bands differ more (NPP r 0.29). On the observed climate it is the vegetation: what to try: water limitation of C4 grass NPP in short wet seasons (the Sahel's 2-3 months), the fire weather's ignition in semi-arid grassland (dry lightning, fuel continuity below ~400 mm rain). Earth is a test analogue: aim for the pattern (southern savannas the main burners, arid margins little), not the numbers.
- [ ] 15-45 N burned area within ~2x of GFED, southern tropics not below GFED by > 30%, totals still in range

## Updates
- 2026-10-16: Created from inbox draft draft-veg-fire-npp-geography-vs-gfed-mod17.md (found by pw204-vegdata).
