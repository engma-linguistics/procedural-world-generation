---
title: "Trade: grain still sails 6,000-10,000 km to some cultures, because bulk goods pay freight alone at sea"
type: task
status: todo
parent: PW-1498
milestone: v4
subsystem: culture
effort: s
impact: low
found_by: lane 235
blocked_by: []
relates: [PW-1505, PW-1532, PW-1533]
refs: ["planet/lineages/trade_flow.py::HAND_KM", "planet/lineages/trade_flow.py::_Frame.cost", docs/review/culture/trade/step4b.md, docs/review/culture/trade/review1.md, docs/review/culture/trade/bought_in.md, docs/review/culture/trade/bought_in/stats.py, "run 3e0eb4 cultures 68, 137, 349", "run 1e97dd culture 753"]
---

## Description
In plain words: the culinary brief's "Bought in" line (PW-1505, lane 235) shows some cultures getting grain from very far by sea.
Examples:
- on 3e0eb4: the first kenku of the south of Simath get grain from 10,604 km; the continental gnomes of the west of Simath from 6,296 and
  7,997 km; the subarctic dwarves of the west of Simath from 6,743 km;
- on 1e97dd (Seven Meals): the half-orcs of the north of Thovalol get grain from 5,595 km.

The far tenth of grain deliveries is 2,300-2,900 km on the four stored L7 runs (3e0eb4, a24559, 1e97dd, 07c755). That is in line
with the review's "thousands of km by water" and with Rome's grain fleet from Africa and Egypt (review1.md section 6). The tail beyond
it is not. Lane 225 left bulk goods out of the merchants' hands at sea (HAND_KM, a JUDGEMENT): their sourced sea cost is freight. That
holds for one hull port to port, but not for a cargo relayed across half the planet.

The shares in that tail are small (1-4% of a culture's people), so it does not dominate any brief. But a reader will trust a line
that says a dwarf hold eats grain shipped 7,000 km.

If it is never done, briefs keep naming continent-crossing grain shipments that no pre-modern grain trade made.

- [ ] source the longest pre-modern bulk grain sea hauls (fetched, not from memory) and set a bound or a relay cost for bulk at sea
- [ ] on the judge runs: grain's far tenth and maximum against main; herders' grain met (PW-1511's measure) not lowered by more than
  the sourced change explains
