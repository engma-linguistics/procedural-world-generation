---
id: PW-1728
title: "Food keeping and flavour: let a preset author a kind's keeping leanings (elves' long ageing, halflings' short horizon)"
type: task
status: done
parent: null
milestone: null
subsystem: food
effort: s
impact: med
found_by: lane308
blocked_by: []
relates: []
refs: [planet/lineages/keeping.py, "planet/lineages/spec.py::BODY_DEFAULT", "planet/lineages/spec.py::parse_body", planet/lineages/samples/dnd.toml, viewer/lineages.html, docs/review/food/flavour-preservation.md, "../culinary-dnd/docs/01-fact-sheets-west-of-the-spine.md:73 (elves: ageing on scales nobody else can attempt)", "../culinary-dnd/docs/01-fact-sheets-west-of-the-spine.md:155 (halflings: preserve for next week, not next year)", "../culinary-dnd/docs/02-fact-sheets-east-and-south.md:118 (dragonborn: straw fuel, wok-logic, no smoking)", "runs a2b637, de1cc6"]
created: 2026-11-11
updated: 2026-11-11
---

## Description
In plain words: keeping.py derives each culture's food keeping and flavour from its land, foods, techs and the body keys a tree already has
(fire, raw_meat, bitter, sweet, capsaicin, salt craving, diet) plus den traits. That covers goblins (strong stomachs: ferments), the cat
peoples (no sweet: sour), the deep and sea folk (no fire). The owner's notes give leanings that no existing body key carries: elves age and
cellar far longer than anyone, halflings keep food only for next week, dragonborn steam and stir-fry and do not smoke, merfolk dry and smoke
only as a shoreline prestige. Today those kinds get the kitchen of whoever lives on the same land, so the culinary book would say an elven
and a human culture on one coast keep food the same way, and a reader would trust it.

Try: an optional inherited body key `keeping = { cellaring = 1.5, smoking = 0.3, ... }` (method id -> multiplier, merged down the tree as
`fit` is), applied in keeping.preservation after the derived weights with its own "because (authored)" reason; set it in the D&D preset
only (Seven Meals is frozen), with the viewer's body editor showing it.
- [ ] a preset can author per-method leanings; each shows as an authored reason on the sheet
- [ ] the D&D preset's elves, halflings and dragonborn read as the notes say on a fresh D&D run

## Updates
- 2026-11-11: Status todo -> done. lane 309 merged
- 2026-11-11: Created from inbox draft draft-keeping-leanings-authored-per-kind.md (found by lane308).
