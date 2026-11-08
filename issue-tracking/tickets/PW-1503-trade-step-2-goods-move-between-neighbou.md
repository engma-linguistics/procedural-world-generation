---
id: PW-1503
title: "Trade step 2: goods move between neighbours and fade with distance by transport mode and era (gifts, barter, markets, merchants, tribute)"
type: task
status: todo
parent: PW-1498
milestone: v4
subsystem: culture
effort: l
impact: high
found_by: lane 211
blocked_by: []
relates: [PW-745, PW-1386, PW-1405]
refs: [docs/review/culture/trade/design1.md, docs/review/culture/trade/review1.md, "planet/lineages/salt_reach.py::_spfa", "planet/lineages/salt_reach.py::TRADE_CAP_KM", planet/humanuse.py, "planet/lineages/polities.py::ROAD_X", "planet/lineages/animals.py::ocean_ships", planet/lineages/attitudes.py, planet/lineages/samples/techtree.toml]
created: 2026-11-07
updated: 2026-11-07
---

## Description
In plain words: the goods from step 1 travel from cultures that have them to cultures that lack them. They fade with the cost
of carrying them, and that cost depends on the cheapest way to carry them there and then: porters, pack animals, carts and roads,
river boats, coastal boats or ships. The design is design1.md, step 2. It can't start before step 1 and decision D-T2 (the unit
of trade).

How it works:
- Generalise salt_reach's cost walk into one walk per good. Each edge of the cost graph costs what the review's sourced
  land : river : sea ratios say, and each culture's techs open the modes: pack_animals, wheel, roads, canoes, sails,
  plank_boats, harbours, navigation, ocean ships.
- Crossing a culture border adds a cost for dealing with strangers. Tolerance lowers it; a war between the two sides that
  century closes the border.
- Supply fades as exp(-cost / L), with one decay length L per value class. Each L comes from the review's sourced distances:
  obsidian's supply zone and fall-off, salt's 450 cost-km, grain overland against grain by water, spices across continents.
- Each flow gets a label for its kind (gifts, barter, market, merchants, tribute), from the two societies it joins.
- Salt reach becomes one good of this pass.

If it is never done, no culture's cuisine can say what it buys in, and D53's trade-mindedness stays a stand-in (openness).
- [ ] trade.json flows per frame (giver, taker, good, amount, cost-km, km, mode, kind); runtime measured, expected a minute
  or two per run at L7
- [ ] judged against the review:
  - fall-off shapes match the obsidian-like curves;
  - bulk goods overland stay within the sourced range;
  - foragers get no more than about half their food by trade;
  - tin moves 1,000 km or more once bronze is known;
  - spices cross continents only with caravans or ships
- [ ] nudge test: a 10% border nudge and a reseed. The top-5 flows per culture should keep their giver and good (report the
  Jaccard overlap)
- [ ] a workbench Trade tab: imports and exports by culture, good, era and kind

## Updates
- 2026-11-07: Created from inbox draft draft-trade-step2-exchange.md (found by lane 211).
