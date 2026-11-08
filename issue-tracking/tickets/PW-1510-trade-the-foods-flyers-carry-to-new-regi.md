---
id: PW-1510
title: "Trade: the foods flyers carry to new regions is an empty record on all three judge runs (no flying people knows a crop)"
type: task
status: done
parent: PW-1498
milestone: v4
subsystem: culture
effort: s
impact: low
found_by: lane 213
blocked_by: []
relates: [PW-1501, PW-1503, PW-1505, PW-912]
refs: ["planet/lineages/trade_flow.py::flyer_foods", docs/review/culture/trade/step2.md, planet/lineages/crops.py, "run 0141d1", "run 3e0eb4", "run 07c755"]
created: 2026-11-08
updated: 2026-11-08
---

## Description
In plain words: Daniel's addition to D65 (PW-1501) was that flying peoples carry foods to new regions, as birds have carried seeds.
Trade step 2 records this (`trade_flow.flyer_foods`). For each flying trading culture and each crop it knows, it lists the farmed land
in and next to its range where the crop is not yet known, and who farms there. On 0141d1, 3e0eb4 (D&D) and 07c755 (Seven Meals) the
record is empty in every frame, because no flying trading people knows any crop.

If nothing is done, the feature exists but shows nothing on the owner's trees, and step 4a and the crop spread have nothing to read.

What to try: a flyer that forages also carries the wild plants of its range. The crop layer `crop_wild` already says where each crop
grows wild. Record a crop that is wild or known in the flyer's range and unknown where neighbouring farmers live. Check it on the three
runs, and say which flyer kinds (aarakocra, kenku, ...) carry what.
- [ ] the record is non-empty on at least one D&D run, and every entry points to a crop the flyer's range has

## Updates
- 2026-11-08: Status todo -> done. Lane 214: flyer_foods now also carries the crops growing wild on the flyer's own cells (crop_wild), to farming trading neighbours where the crop is neither known nor wild; each entry says from: known or wild. Non-empty on all three runs (eras with a record: 21 / 21 / 23 of 26 on 0141d1 / 3e0eb4 / 07c755); all entries are the aarakocra's, from wild plants (e.g. 3e0eb4: alliums, wheat, pulses, oil seeds, pseudograin). docs/review/culture/trade/step3.md, tests/test_trade_routes.py::test_flyers_carry_the_wild_foods_of_their_range.
- 2026-11-08: Created from inbox draft draft-trade-flyer-foods-empty.md (found by lane 213).
