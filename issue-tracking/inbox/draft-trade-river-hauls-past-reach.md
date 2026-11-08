---
title: "Trade: dear goods now take the rivers and still go past their sourced reach (spices' far tenth 9,700-14,600 km)"
type: task
status: todo
parent: PW-1498
milestone: v4
subsystem: culture
effort: m
impact: med
found_by: lane 225
blocked_by: []
relates: [PW-1529]
refs: [docs/review/culture/trade/step4b.md, docs/review/culture/trade/step4a/judge.py, "planet/lineages/trade_flow.py::HAND_KM", "planet/lineages/trade_flow.py::RIVER_DOWN", "planet/lineages/trade_flow.py::RIVER_UP", "planet/lineages/trade_flow.py::TOLL", "planet/lineages/trade_flow.py::_Frame.cost", "run 3e0eb4", "run 0141d1", "run 07c755", "Pearson 1987 The Portuguese in India p. 41", "Pliny NH 6.101"]
---

## Description
In plain words: lane 225 made a sea haul cost its merchants' hands (a share of value per sea km, step4b.md). The dear goods then moved
from the sea to the rivers: spices' flows are now mostly river hauls (0.83 of them on 3e0eb4, 0.64 on 0141d1, 0.50 on 07c755, against
under 0.1 in main), and spices' median is still 5,200-8,200 km, the far tenth 9,700-14,600 km, past the sourced ~8,000 km of pepper from
Malabar to Rome (Pliny NH 6.101; Pearson's price chain). A reader of the culinary brief would see spices crossing a continent by river.

Why: a river haul's per-km cost is ORBIS's river freight (1/8 of a donkey downstream, 1/4 upstream); the land fall-off length is the
whole overland markup, and the tolls at each border are 10% at the median tolerance. Lane 225 tried charging rivers the same hands rate
(3,000 km per e-fold) on 3e0eb4: the long-haul layer fell to 1,139 stretches an era (from 1,472) but herders' grain met fell from 0.1266
to 0.1083, because grain goes by river too.

What to try: first measure what a long spice flow is made of (km by river, by sea, by land; borders crossed) on 3e0eb4. If the river legs
cross few borders (one culture holding a long river), a river haul's hands per km for middling and dear goods only (bulk as freight, as
at sea) is the same mechanism as at sea; check herders' grain and the land-nudge steadiness (about 0.7 or more) on the three runs.

- [ ] a breakdown of spices' far flows by mode and borders on 3e0eb4
- [ ] if rivers carry them unbroken, the hands on river legs for middling and dear goods; spices' far tenth within ~8,000-10,000 km
