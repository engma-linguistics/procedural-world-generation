---
title: Crop fronts ignore day length and season regime (maize north, wheat into summer-rain lands)
type: task
status: todo
parent: null
milestone: v2
subsystem: food
effort: m
impact: med
found_by: lane-157
blocked_by: []
relates: []
refs: [planet/lineages/animals.py::Stock._front, planet/lineages/crop_defs.py::_range, docs/review/food/crops-origins/round1.md, docs/review/food/crops-origins/round1_sources.md]
---

## Description
**In plain words:** on Earth, crops moved slowly when they had to change seasons. Maize crept north at about 1.3 km a year, about 92 years for each degree of latitude (Merrill et al. 2009 PNAS). The winter-sown wheat and barley and the summer-sown millets took 5–6 kyr to swap between western and eastern Eurasia (Liu et al. 2019 QSR §4.2–4.3). The Andean potato is short-day; the potato that took in Europe came from long-day Chilean stock (FAO 2008).

In the model, a crop's front (`Stock._front`) moves at its own km/yr over peopled land. Where it can be grown depends only on temperature, rain and height windows (`crop_defs._range`). So nothing slows a crop crossing latitude or rain season.

Candidate fix: a step cost on the front where the cell's season regime differs from the homeland's. That could be the Köppen dry-summer vs summer-rain class, or a latitude band, the way the contact animals already use `BARRIER_ENTER`. One sourced number would be the slowdown factor, for example from Merrill's 1.3 km/yr maize rate against the ~1 km/yr Neolithic front.
- [ ] a crop entering the other season regime is slowed, with a sourced factor
- [ ] dnd and seven_meals pass the robust suite with no new brittle peoples
