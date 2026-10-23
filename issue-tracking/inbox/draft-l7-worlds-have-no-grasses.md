---
title: "The four L7 showcase worlds' vegetation has no grasses: pasture is ~0 on their steppes"
type: task
status: todo
parent: null
milestone: v2
subsystem: surface
effort: s
impact: med
found_by: lineages-lane-4
blocked_by: []
relates: [PW-103]
refs: [planet/vegetation.py, planet/gameattrs.py, "worlds 1144ce, 3e0b0a (and likely 31926a, 91448a)", planet/lineages/land.py]
---

## Description
The lineages land use (lane 4) reads `gameattrs.world_layers` grazing. On the L7 showcase worlds that is ~0 everywhere:
- 1144ce steppe (BSh/BSk, 5254 cells): grazing p50 0.0, p90 0.0, max 1.6 of 5. 3e0b0a's is the same.
- On 119973 (L6), steppe grazing is p50 3.8.

The cause is upstream. 1144ce's `meta.vegetation.pfts` is `['TeNE', 'BoNE', 'BoNS', 'Moss', 'WetH', 'Sph']` (from_history): no C3G/C4G grasses, shrubs or tropical trees. Its steppe shows `veg_C3G = veg_C4G = 0` with 85% "plant cover", mostly moss. 119973 has all 19 plant types.

This looks like a world finished before a vegetation change, or a history-mode path that keeps only the plant types of some reference epoch. It breaks pasture, foraging, fuel and the satellite view's grassland on those worlds.

The lineages lane works around it rather than stretching noise: a living good on under 2% of the land is left out as missing (`land.MISSING_SHARE`), and the report says so. Orcs therefore get no pasture pull on these worlds.
- [ ] find why 1144ce's vegetation has 6 PFTs; refinish or fix the path
- [ ] grazing on the L7 steppes comparable to 119973's
