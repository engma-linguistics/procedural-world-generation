---
id: PW-1664
title: L8 split still has a third fewer coastal towns than L7 after the km fixes, while inland has more
type: task
status: todo
parent: PW-1198
milestone: v5
subsystem: peoples
effort: m
impact: med
found_by: lane272c-pw1630
blocked_by: []
relates: [PW-1630, PW-1631, PW-1265, PW-1584]
refs: ["planet/lineages/ladder.py::WATER_CELL_KM", "planet/lineages/ladder.py::RICH_KM", planet/lineages/settlements.py, docs/review/refine-l8/split.md, "runs 732ed6 and 3413e1 (L7 on 899985), f465d8 and 393622 (split on 9cf1c3), lane 272 scratch, may be gone", "townband.py, townlife.py, bestsite2.py (lane 272 scratch)"]
created: 2026-11-10
updated: 2026-11-10
---

## In plain words
On the finer L8 grid the history still ends with fewer towns on the coast than the same world on L7, though the model
now finds roughly the same number of good coastal sites. Inland, L8 has more towns. A reader comparing coasts across grids
would take that for a fact about the world.

## Description
After lane 272's ladder fixes (split.md section 7.1), Earth-like A, L7 732ed6 against split 393622 (old split f465d8):
- towns and cities within ~60 km of the fine sea 15.2% (L7) / 10.2% (new) / 9.1% (old); on the coast 7.6 / 5.2 / 4.4%;
  islands with a town 22 / 13 / 11.
- places that were ever a town or city: coast band 1,384 / 869 / 724, but inland 7,984 / 9,233 / 8,701. Founded median
  3.0 kyr on both splits against 3.8 (L7) in the band.
- the band's sedentary people 136 / 119 / 106 M, and its share of the best town sites at the final frame 11.8 / 13.2 / 11.0%,
  so the sites are there and the people are about 87% of L7's: the shortfall is in turning coastal people into towns.
Diagnosis so far: not the town rule's site choice (best-site share matches), not the ladder's km reads (fixed). Remaining
candidates, cheapest first: (a) the refine's soils (fertile within 60 km of the sea 0.539 L7, 0.439 L8: the soils draft);
(b) town founding reads per-cell heads on a quarter-area cell, which hits the coast hardest because a coastal cell holds
less land; (c) draw noise: re-roll 2-3 tries of both before calling it signal.
- [ ] after the soils draft lands, rerun the split on 9cf1c3 and re-read coast share, band towns and islands
- [ ] if still short, check (b) with the founding thresholds expressed in km2, not per cell

## Updates
- 2026-11-10: Created from inbox draft draft-l8-coast-towns-remaining-gap.md (found by lane272c-pw1630).
