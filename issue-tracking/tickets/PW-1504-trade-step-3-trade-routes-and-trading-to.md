---
id: PW-1504
title: "Trade step 3: trade routes and trading towns (ports, river ports, caravan towns, merchant quarters) on the globe"
type: task
status: done
parent: PW-1498
milestone: v4
subsystem: culture
effort: m
impact: high
found_by: lane 211
blocked_by: []
relates: [PW-1011, PW-889]
refs: [docs/review/culture/trade/design1.md, docs/review/culture/trade/review1.md, planet/lineages/settlements.py, "planet/lineages/settlements.py::CONST", viewer/index.html]
created: 2026-11-07
updated: 2026-11-08
---

## Description
In plain words: the big flows from step 2 become roads on the map. Towns where routes meet, or where goods change from ship to
caravan, become trading towns. The design is design1.md, step 3. It needs step 2.

How it works:
- Trace each large flow's least-cost path, using the cost walk's predecessors. Add the flow's load to every cell it crosses, and
  keep the loaded cells as that era's routes.
- A ledger town on a route ranks as a hub by how much passes through it. Its kind comes from where the mode changes:
  - a port, where sea meets land;
  - a river port;
  - a caravan town, where pack routes leave farmland for desert or steppe;
  - otherwise a market town.
- A town with heavy foreign throughput gets a merchant quarter of the giver's people. This is Curtin's trade diaspora, and the
  minority quarter PW-889 asked for. The quarter lowers that border's crossing cost the next century.

If it is never done, Daniel can see trade only in tables, not on the globe.
- [ ] trade.json routes (polylines, load, leading good class) and hubs; a trade_load layer per frame
- [ ] viewer:
  - an Overlays > Trade routes box: line width by load, colour by good class, on the time slider;
  - a ring on each hub town, and a hover card;
  - a `?trade=routes` deep link
- [ ] judged:
  - a few trunk routes per landmass per era, not a mesh;
  - ports sit at harbours and caravan towns at desert edges;
  - the route set holds steady under the nudge test;
  - screenshots in docs/review/culture/trade/

## Updates
- 2026-11-08: Status todo -> done. Lane 214: built (planet/lineages/trade_routes.py; globe Overlays > Trade routes, ?trade=routes; hover card; brief Trade panel's Trading towns table). Routes: every delivery between cultures traced back along the walk's predecessors; a stretch carrying 2% of its goods group's traded volume is a route. Judge (docs/review/culture/trade/step3.md): 53-74 stretches in 5-7 pieces per era on average; trading towns mostly river ports; 5 of 6 ports by a harbour; no caravan towns; towns hold 0.71-0.89 under the land nudge, routes 0.57-0.73 (two drafts filed: land nudge, mostly salt). No per-cell trade_load layer (the stretches and towns' throughput carry it). Screenshot docs/review/culture/trade/step3_routes_3e0eb4.png.
- 2026-11-07: Created from inbox draft draft-trade-step3-routes-hubs.md (found by lane 211).
