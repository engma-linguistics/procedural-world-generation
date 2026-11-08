---
id: PW-1500
title: "Trade D-T2: what trades with what: whole cultures, map cells, or towns?"
type: task
status: needs-decision
parent: PW-1498
milestone: v4
subsystem: culture
effort: xs
impact: med
found_by: lane 211
blocked_by: []
relates: [PW-670, PW-1011]
refs: [docs/review/culture/trade/design1.md, docs/review/culture/trade/review1.md, planet/lineages/cultures.py, planet/lineages/settlements.py, "planet/lineages/salt_reach.py::_spfa", "planet/lineages/cuisine.py::culture_cells"]
created: 2026-11-07
updated: 2026-11-07
---

## Description
In plain words: goods have to move between *something*, and the model has three candidates:
- cultures: a few hundred per run, and what the culinary brief describes;
- map cells: about 55 km each at the showcase level, where the land goods and rivers live;
- towns: from the settlement ledger, only in the last ~12 kyr and only for settled peoples.

Options:
- A. Cultures. One supply and one want per culture per era, and flows between neighbouring cultures. This is the cheapest. But a
  big culture's coast and its desert interior would trade as one, and routes couldn't be drawn.
- B. Cells for goods and costs, using the same cost walk salt reach already uses. Results are summed to cultures for the brief
  and the Trade tab. Towns are only the hubs where routes meet (step 3).
- C. Towns. Trade happens only between places in the ledger, as a network. This is closest to markets and merchants (central
  places). But foragers and herders have no towns, so they would have no trade at all. That goes against the review: hxaro,
  forager-farmer and steppe-sown exchange are among the oldest and commonest kinds.

Trade-offs: B costs about 16 cost walks per frame, a few minutes after a run at L7. In return it keeps foragers and herders in,
and it puts routes on real rivers and coasts. **My lean: B.** If this is never decided, step 2 can't start.

## Updates
- 2026-11-07: Created from inbox draft draft-trade-d2-unit-of-trade.md (found by lane 211).
