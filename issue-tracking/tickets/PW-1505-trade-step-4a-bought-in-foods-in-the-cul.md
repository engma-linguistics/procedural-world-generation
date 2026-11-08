---
id: PW-1505
title: "Trade step 4a: bought-in foods in the culinary brief (what, from whom, how far, by what road)"
type: task
status: todo
parent: PW-1498
milestone: v4
subsystem: food
effort: m
impact: high
found_by: lane 211
blocked_by: []
relates: [PW-692, PW-728, PW-744, PW-805, PW-912, PW-984]
refs: [docs/review/culture/trade/design1.md, docs/review/culture/trade/review1.md, "planet/lineages/brief.py::NOT_MODELLED", "planet/lineages/cuisine.py::sheet", planet/lineages/salt_reach.py]
created: 2026-11-07
updated: 2026-11-07
---

## Description
In plain words: the project's end goal is who eats what, and real cuisines are full of bought-in food. Examples:
- salt;
- pepper;
- wine where no vine grows;
- salt fish far inland;
- grain eaten by herders;
- tea along a tea road.

The design is design1.md, step 4a. It needs step 2; step 3's routes supply the "by what road" part.

The cuisine sheet's staple, drink and fuel lines read the culture's food imports from trade.json. This fills the brief's
`trade_reach`, which is null today and listed as not modelled. Each bought-in food gets its giver, distance and mode, so PW-984
(food words travel with food) has a path to follow. It closes most of PW-744 (cuisine plants as trade goods) and of PW-805 (salt
goods in a trade table).

If it is never done, the brief keeps describing every culture as eating only what its own land grows. No settled culture in the
review does that.
- [ ] cuisine sheet: a "Bought in" line; the brief's trade_reach filled; BRIEF_VERSION bumped
- [ ] checked on the D&D showcase and the stress trees: herders' grain, inland salt, and how far wine and spice reach all make
  sense against the routes

## Updates
- 2026-11-07: Created from inbox draft draft-trade-step4a-culinary-imports.md (found by lane 211).
