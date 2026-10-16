---
title: "Vegetation: sclerophyll scrub spreads into steppe, savanna grassland and warm temperate forest since the fuel-age fire (PW-234)"
type: task
status: needs-decision
parent: null
subsystem: surface
effort: s
impact: med
found_by: vegbatch
blocked_by: []
relates: [PW-234, PW-220, PW-231]
refs: [planet/vegetation.py, tools/veg_check.py, docs/review/vegetation/batch-2026-10-16.md]
---

## Description
PW-234 gave shrubs a slowly decaying dead fuel (SLOW_FUEL 0.5) and sclerophyll shrubs (SclS) a resprouter's fire survival (0.8 -> 0.9). Maquis now burns every ~20-50 yr and stays scrub, but SclS also became the most fire-tolerant woody type wherever it is viable, and its own fuel feeds the fire that keeps trees out (a shrub-fire feedback, as real fire-prone shrublands have):
- L7 world from run a1d3b9 @ 1000 Myr (keyframe; before dd66bf / after 7d3c84, deleted after the batch): dry sclerophyll scrub 1980 -> 4672 cells (of 52k land), from short-grass steppe (1127), tropical grassland (618), temperate woodland (567); warm temperate mixed forest -> temperate scrub and thicket (522); mean tree cover 40.4 -> 37.8%, SclS cover 4.9 -> 10.8%. Zoom at 32.0, -80.5 (600 km @ 2 km): maquis 17 -> 62% of the land, trees 17 -> 4%, woodland and steppe mostly gone.
- Earth (observed climate): ~3 Mkm2 more shrubland (tropical grassland in Botswana/Zambia and short-grass steppe -> "dry sclerophyll scrub"; some Chaco and N India forest -> thicket); agreement 60.6 -> 59.9%.
Options:
- (A) Keep (resprouting sclerophylls are fire winners; Earth agreement barely moves; the potential-vegetation "shrubland" Earth has is mostly called grassland by the model anyway).
- (B) SclS survival back to 0.8: shrub expansion mostly gone, Earth agreement 60.0%, maquis fire return median 49 yr, but Mediterranean cells 124 -> 79 (the Mediterranean box 81 -> 41) and burned share in grassy types 89%.
- (C) Keep 0.9 and narrow where SclS lives instead: its envelope (coldest month -5..18 C, GDD5 >= 1500) admits cold-winter steppes and subtropical summer-rain savannas where the real shrubs are deciduous thorn or sagebrush; e.g. a summer-drought or poor-soil condition for SclS (soils now give fertility).
Lean: C, after checking it doesn't just move the problem.
