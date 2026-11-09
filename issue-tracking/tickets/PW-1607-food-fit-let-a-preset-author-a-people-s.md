---
id: PW-1607
title: "Food fit: let a preset author a people's fit (a body `fit` table and an alcohol flush share), so owner canon and drink-flush peoples can be said"
type: task
status: todo
parent: PW-856
milestone: v5
subsystem: food
effort: s
impact: med
found_by: lane256
blocked_by: []
relates: [PW-905, PW-692]
refs: ["planet/lineages/food_fit.py::fit", "planet/lineages/spec.py::parse_body", "planet/lineages/spec.py::BODY_DEFAULT", docs/review/food/lane256.md, planet/lineages/samples/dnd.toml]
created: 2026-11-09
updated: 2026-11-09
---

## Description
In plain words: the food-fit spectrum (lane 256, food_fit.py) is worked out only from the body keys the presets already carry (milk,
sweet, capsaicin, raw_meat, cellulose, gut, grain, bitter, toxic, diet). A preset cannot yet say "this people is poorly suited to
alcohol" or "this people thrives on X" directly. So:
- The East Asian-style alcohol flush (ALDH2*2, about half of East Asians carry it; Wikipedia, ALDH2) cannot be given to a human people as a share.
- Owner canon (culinary-dnd master reference §7) says the cat peoples "barely drink" and have an inhaled scent intoxicant instead, and a
  third feel nothing. Today they get "poorly suited to alcohol" only through the cat-like toxicity marker.
- Grapes and raisins are toxic to dogs (Merck), but no body in the presets marks a canid, so the row is left out.

What breaks if never done: every people's fit is the derived default. The culinary side has to overrule it by hand in the book.
- [ ] a body `fit` table (food id -> thrives | tolerates | poor | harmful) that wins over the derived row, inherited like other body keys; the viewer's body editor must cope with a table value
- [ ] an `alcohol_flush` share (0..1) read as "tolerates, x% flush"

## Updates
- 2026-11-09: Created from inbox draft draft-food-fit-authored-overrides.md (found by lane256).
