---
id: PW-1530
title: "Trade: with every good seeking to the end and a local layer, ~800 trading towns at the present on 3e0eb4 (41 before)"
type: task
status: todo
parent: PW-1498
milestone: v4
subsystem: culture
effort: s
impact: med
found_by: lane 222
blocked_by: []
relates: [PW-1515, PW-1519, PW-1504]
refs: [docs/review/culture/trade/step3d.md, "planet/lineages/trade_routes.py::Loads._hubs", "planet/lineages/trade_routes.py::LOCAL_SHARE", "run 3e0eb4", "run 0141d1", "run 07c755"]
created: 2026-11-08
updated: 2026-11-08
---

## Description
In plain words: a settlement-ledger town that any trade route passes through counts as a trading town. Lane 222 made every good keep
looking for sources until none is left, and split the routes into a long-haul layer and a local layer, each judged on its own volume.
The route stretches went from ~330-540 an era to ~2,100-2,350, so the trading towns went from 41 at the present on 3e0eb4 to 804
(622 river ports, 136 market towns, 34 caravan towns, 12 ports). On the globe the rings now crowd the river valleys.

If nothing is done, "trading town" stops meaning much: nearly every river town is one, and merchant quarters (which lift tolls next
era) follow the same rule.

Options (for Daniel or the coordinator):
- A: a trading town needs a long-haul route through it (the hub flag `long` already exists; 213 of the 804 at the present).
- B: keep both layers, but rank towns by throughput and show only the top share, local ones as smaller rings.
- C: leave it: local exchange is real and every market town on a river trades.

## Acceptance
- [ ] A ruling on A / B / C; if A or B, the trading-town count per era on the three judge runs is reported before and after.

## Updates
- 2026-11-08: Status needs-decision -> todo. Coordinator 11-08: option A for 'trading town' (needs a long-haul route; merchant quarters follow it), with other route towns kept as market towns drawn small (B's ranking). Next trade lane, with PW-1522 and PW-1529.
- 2026-11-08: Created from inbox draft draft-trade-towns-hundreds-per-era.md (found by lane 222).
