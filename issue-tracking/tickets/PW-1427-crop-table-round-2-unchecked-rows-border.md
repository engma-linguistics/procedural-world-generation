---
id: PW-1427
title: Crop table round 2 - unchecked rows, borderline dates and four more foods
type: task
status: todo
parent: null
milestone: later
subsystem: food
effort: m
impact: med
found_by: lane-157
blocked_by: []
relates: []
refs: [planet/lineages/crop_defs.py, planet/lineages/samples/techtree.toml, docs/review/food/crops-origins/round1.md, docs/review/food/crops-origins/round1_sources.md]
created: 2026-11-03
updated: 2026-11-03
---

## Description
**In plain words:** lane 157 checked the crop table against Larson et al. 2014 PNAS Fig. 2 and other sources. It fixed beans and quinoa (7.0 to 5.0 kyr) and added soybeans, cowpeas and date palms (36 rows). Still open:
- **Not checked yet:** tropical spices, sap sugar and beet, cooking greens, onions and garlic, vanilla, oats. Each needs a sourced first-cultivation date.
- **Borderline dates** (round1_sources.md §1):
  - tomato: 5.0 now; ~7.0 from a single genetic estimate (Razifard 2020).
  - oil seeds: 6.0 now; flax is ~9.5, so either split flax out or source the sesame date.
  - foxtail millet: 10.0 now; it holds only if the row is relabelled "foxtail and broomcorn millet" (Lu 2009).
- **Foods to add**, with dates read off Larson Fig. 2 except breadfruit and coffee:
  - mung bean, 4.0
  - Old World melons and cucumbers, 4.0
  - breadfruit, at least 3.1 (Pawley; carried by the Lapita colonists)
  - coffee as its own row, ~0.55 (weak sources; the "tea, coffee" row is tea at 2.5)
- **Foods with no source opened yet:** citrus, mango, apple, fig, teff, finger millet, buckwheat.

Each new row also needs a `crop_<id>` entry in techtree.toml, as the lane 157 rows have.

## Updates
- 2026-11-03: Created from inbox draft draft-crop-rows-round2.md (found by lane-157).
