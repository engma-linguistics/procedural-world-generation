---
id: PW-1748
title: A culture's crops and herds include other peoples' fields on its land, so its kitchen lists food its people does not grow
type: task
status: todo
parent: null
milestone: null
subsystem: food
effort: s
impact: med
found_by: lane309
blocked_by: []
relates: []
refs: ["planet/lineages/cuisine.py::profile", "planet/lineages/cuisine.py::_bits_on", "planet/lineages/kitchen_time.py::_how", "planet/lineages/keeping.py::inputs", "runs a2b637, de1cc6 (copies in a scratch dir, since deleted)", docs/review/food/flavour-preservation.md]
created: 2026-11-11
updated: 2026-11-11
---

## Description
In plain words: cuisine.profile takes a culture's crops and herds from the frame's crop_known / animal_known layers on its cells (any
people's fields there, from 10% of its cells). It zeroes the farm share when the culture's people knows no crop tech, but it keeps the
crop list. The kitchen-through-time view (kitchen_time.py) shows how often that list is someone else's: on a2b637 the steppe orcs of west
Huramom (culture 268) gain wheat 4,000 years ago, olives, beans, greens and peanuts later, each marked "another people's, on its land"
(its people took wheat up only ~100 years ago). The same lists feed the sheet's staple line, its flavour (sweet, fatty and hot crops) and
its keeping (grain and vegetables to keep).

If never done: the culinary book would give a culture olives, peanuts or wheat in its staple, its sweet and fatty tastes and its stores
when the history says its own people does not grow them, and a reader would trust the sheet.

Try: in profile, keep a crop or herd only where the culture's people knows its tech (crop_<id> / animal_<id> in meta.techtree.known by
the era) or the tree has no such tech; list the rest as "grown by neighbours on its land" (and maybe as bought-in food).
- [ ] on a2b637 culture 268 at 4,000 years ago, wheat is not among its own crops; it shows as a neighbour's

## Updates
- 2026-11-11: Created from inbox draft draft-culture-crops-include-other-peoples-fields.md (found by lane309).
