---
title: "A trading town is credited to a culture of another people than the one living in it"
type: task
status: todo
parent: null
subsystem: culture
effort: s
impact: med
found_by: lane312
blocked_by: []
relates: [PW-1504, PW-1659]
refs: ["planet/lineages/trade_routes.py::frame_view", planet/lineages/settlement_view.py, viewer/globe/trade.js, "run de1cc6 (Seven Meals on 2762ba)", docs/review/viewer/lane312.md]
---

## Description
On run de1cc6 at the present, site 29063 ("the south-west of Nijaser", lat 2.227, lon 83.418) is a town whose people are 100% humans
(settlements.json `who`, held by the humans since its founding 1,100 years ago). The exchange's hub for that same site
(`GET /api/trade?routes=1&ago=0`) names it a river port of the culture Bumb Niynumb, which is a half-orc culture. The half-orcs
live in the same cell, but outside the town. The Trade routes hover card and the new settlement view (lane 312) both show
"a river port of Bumb Niynumb". A reader will take that to mean the half-orcs run the town's trade.

If this is never fixed, the hover card and the settlement view keep telling readers that a town's port belongs to a people who
do not live in it. The tongues ledger, which picks a trade language from the trading towns' cultures, may then weigh the wrong
people's tongue.

Check how the hub's culture is chosen (probably the cell's culture with the most people). Prefer the culture of the site's holder
when it has a deme in the cell.
- [ ] the hub's culture is one of the town's own peoples' cultures, whenever one lives in the cell
- [ ] a test with a town of one people in a cell where another people's culture has more heads
