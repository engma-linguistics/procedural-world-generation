---
id: PW-1515
title: "Trade routes are nearly all salt: grain and metal make no routes, and no caravan town appears on the judge runs"
type: task
status: todo
parent: PW-1498
milestone: v4
subsystem: culture
effort: s
impact: med
found_by: lane 214
blocked_by: []
relates: [PW-1504, PW-1505, PW-1511]
refs: [docs/review/culture/trade/step3.md, docs/review/culture/trade/step2.md, "planet/lineages/trade_routes.py::Loads.finish", "planet/lineages/trade_routes.py::Loads._hubs", "planet/lineages/trade.py::ledger_at", "run 0141d1", "run 3e0eb4", "run 07c755"]
created: 2026-11-08
updated: 2026-11-08
---

## Description
In plain words: on the three judge runs (0141d1, 3e0eb4, 07c755), the trade routes of step 3 are mostly salt by sea and river from 6,000
years ago on (e.g. 0141d1 6 kyr ago: 115 of 121 route stretches are salt; 3e0eb4 from 6 kyr ago on: all of them). Grain and metal make no
routes after 9 kyr ago, and fine goods only in some eras. No caravan town appears on any run, and ports are rare (6 town-eras on 3e0eb4,
none on the others); most trading towns are river ports. Baseline: before step 3 there were no routes.

Why (likely): each kind of goods' route is measured against that kind's own world trade. Salt is lacked only far (over 300 km) from salt
(step 1), from few sources, so its flows share long roads. Grain and metal mostly go between neighbours (step 2: middling goods' median
19-44 km), so no single road carries 2% of them.

If it is never done, the globe's Trade routes overlay tells Daniel that these worlds trade almost only salt, and step 4b (spread along
busy routes) would follow salt roads alone.

What to try: compare against the review's cases (R§4: tin, spice, grain to cities by water); check whether towns' grain (central places)
should travel further by river; measure routes per kind against each kind's own top stretches rather than one shared 2% bar; check the
caravan-town rule's inputs (Koppen B cells beside farmed towns on a land route).
- [ ] the overlay shows at least food and one other kind besides salt in most eras with towns, or the doc explains why the worlds do not trade them far

## Updates
- 2026-11-08: Created from inbox draft draft-trade-routes-mostly-salt.md (found by lane 214).
