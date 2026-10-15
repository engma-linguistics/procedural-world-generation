---
id: PW-231
title: "Vegetation: C3/C4 grass crossover at 25 deg on observed climate (obs ~30-35); simple temperature nudges don't move it cleanly"
type: task
status: todo
parent: null
subsystem: surface
effort: s
impact: low
found_by: smalls2
blocked_by: []
relates: [PW-205]
refs: [planet/vegetation.py, tools/veg_check.py]
created: 2026-10-15
updated: 2026-10-15
---

## Description
Rest of PW-205. tools/veg_check.py: "C4 share < 50% from latitude" is 25/25 (N/S) on the observed climate, 30/30 on the model's (target ~30-35, Still et al. 2003). Two nudges tried on branch smalls2, neither taken:
- C4G temperature curve (10, 25, 38, 50) -> (8, 22, 38, 50): crossover N 25 -> 30, S unchanged; but potential-vegetation agreement 62.5 -> 61.7%, savanna/tropical grass 21.4 -> 22.6 Mkm2 (already high), burned area 5.1 -> 5.4.
- C3G heat penalty (-2, 12, 25, 38) -> (-2, 12, 22, 36): no change to the crossover or the rest.
So the C3 grasses at 25-35 deg probably win on their cool-season growth (C4 is leaf-on only above 10 C) rather than on summer heat. Look at what C3G and C4G each get by month in grassy cells at 25-35 deg (e.g. the US southern plains, N India, S Africa's highveld), and whether the crossover should come from the rain's season (summer-rain grasslands are C4 even where winters are cool) instead of temperature.
- [ ] crossover 30-35 deg on the observed climate without losing potential-vegetation agreement

## Updates
- 2026-10-15: Created from inbox draft draft-c4-crossover-nudges.md (found by smalls2).
