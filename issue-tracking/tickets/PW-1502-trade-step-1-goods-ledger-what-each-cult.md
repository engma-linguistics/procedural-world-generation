---
id: PW-1502
title: "Trade step 1: goods ledger: what each culture's land gives in surplus and what it lacks, per era"
type: task
status: done
parent: PW-1498
milestone: v4
subsystem: culture
effort: m
impact: high
found_by: lane 211
blocked_by: []
relates: [PW-744, PW-805, PW-728]
refs: [docs/review/culture/trade/design1.md, docs/review/culture/trade/review1.md, "planet/lineages/land.py::GOODS", planet/lineages/seafood.py, planet/lineages/crop_defs.py, planet/lineages/animals.py, planet/lineages/fuels.py, "planet/lineages/landuse.py::frame_inputs", "planet/lineages/cuisine.py::culture_cells", planet/lineages/samples/techtree.toml]
created: 2026-11-07
updated: 2026-11-08
---

## Description
In plain words: before anything can be traded, each culture needs a list of what its own land gives in plenty and what it
lacks, for example "salt, wool, horses; lacks grain and metal". The design is design1.md, step 1.

Build `planet/lineages/trade.py::goods` as a read-out after the run, like fuels.py.
- It maps the existing land goods, crops, herds and fuels onto about 16 trade goods in three value classes: bulk, middling and
  precious (see review1.md's section on transport costs and value per weight).
- Surplus = (land value) x (heads working it, from eraq) x (a know gate: the tech or crop that unlocks the good).
- Want comes from the way of life and the techs known:
  - farmers want salt, and tin and copper once they have smiths;
  - herders want grain;
  - towns want grain and fuel;
  - foragers want ornaments, and starch where farmers are near.
- No fitted numbers: every entry points to the layer it comes from.

If it is never done, the brief keeps `trade_reach: null`, and none of the later steps (exchange, routes, bought-in foods) can start.
- [ ] trade_goods.json per culture per frame, and meta.trade.goods; takes seconds per run at L7
- [ ] the brief's culture sheet gets a "has / lacks" line
- [ ] a globe layer "Trade goods": pick a good to see surplus against lack
- [ ] checks:
  - salt-poor interiors lack salt (matching the brief's salt reach);
  - tin is held by few cultures and lacked by most bronze users;
  - steppe herders lack grain.

## Updates
- 2026-11-08: Status todo -> done. Lane 212 merged (suite 1075): goods ledger read-out, step1.md.
- 2026-11-07: Created from inbox draft draft-trade-step1-goods-ledger.md (found by lane 211).
