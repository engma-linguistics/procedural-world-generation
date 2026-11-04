---
title: Herd animals still cross open sea to strangers before ocean ships, and never cross oceans after 1492
type: task
status: todo
parent: null
milestone: v2
subsystem: food
effort: s
impact: med
found_by: lane-157
blocked_by: []
relates: []
refs: [planet/lineages/animals.py::Stock._sail, planet/lineages/animals.py::Stock._sail_crop, planet/lineages/animals.py::Stock._ocean, planet/lineages/animal_defs.py::craft_ladder, docs/review/food/crops-origins/round1.md]
---

## Description
**In plain words:** lane 157 fixed the crops' sea crossings. Before the ocean-going ships, a crop crosses long open sea only with colonists going to their own land, and passes between peoples only over a strait. From 1492 on (0.53 kyr before the present, in a renaissance or later present), it reaches every peopled landmass. The herd animals still use the old rule (`Stock._sail`):
- From 3 kyr ago, any people that crews a sailing ship carries horses or cattle up to 2,500 km of open sea, onto anyone's land.
- There is no Columbian exchange. On Earth, horses, cattle and pigs reached the Americas from 1493.

Two related points:
- `craft_ladder` dates its boats in absolute kyr and never reads `meta.era`. A stone-age present still has "sailing ships" 3 kyr before it. This touches the peoples' own crossings too (`craft_for_people`).
- The best-craft-only rule in `_sail`: once planked boats exist, only peoples that crew them carry animals at all.

Candidate fix: apply `_sail_crop` / `_ocean` to animals too. For peoples, gate the craft rungs on the era.
- [ ] animals follow the same colonist/strait/ocean-ship rules as crops
- [ ] robust suite: no new brittle peoples
