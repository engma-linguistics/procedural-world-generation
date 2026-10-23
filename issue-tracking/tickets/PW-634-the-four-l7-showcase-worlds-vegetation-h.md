---
id: PW-634
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
created: 2026-10-23
updated: 2026-10-23
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

## Updates
- 2026-10-23: Root cause found (bug-hunt lane): not stale worlds and not a vegetation bug. Each world's PFTs
  are exactly `vegetation.unlocked_at(run plant_groups, t)` with current code: the plant groups appear late in a
  run (flowering trees/shrubs at ~0.73, grasses ~0.85, C4 ~0.94 of the span; 1 Gyr runs reach full flora at
  772-876 Myr), and `highlights.representative_time` (`--at auto`, `planet make`) ignored them, picking 308-748 Myr.
  Fix: `representative_time(..., plant_groups=)` picks only among frames once the last group has appeared
  (medians still the whole stretch's); make and `--at auto` pass the run's groups. simulate outputs unchanged.
  Worlds with <19 PFTs (need re-slicing at a new pick, coordinator): 6 PFTs 1144ce 3e0b0a 31926a 7082f5 81aced
  a5a387 c00ebf 28442c; 17 (no C4G/Succ) 91448a 607540. New picks: 1112ef 844, 6a0029 896, 396621 936,
  f9e085 960, 172922 996, 343058 956, 2b0b65 920, 0ecb0d 856, bf5ee9 1636 Myr. Trade-off filed as a draft
  (draft-flora-arrives-late-in-runs.md).
- 2026-10-23: Created from inbox draft draft-l7-worlds-have-no-grasses.md (found by lineages-lane-4).
