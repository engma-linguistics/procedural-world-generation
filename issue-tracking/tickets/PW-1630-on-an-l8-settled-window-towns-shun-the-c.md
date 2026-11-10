---
id: PW-1630
title: On an L8 settled window, towns shun the coast, islands lose their towns and cities fall to a third (measured; evidence for PW-1627)
type: task
status: todo
parent: PW-1198
milestone: v5
subsystem: peoples
effort: m
impact: med
found_by: lane267b-pw1265
blocked_by: []
relates: [PW-1627, PW-1265, PW-1584]
refs: [docs/review/refine-l8/split.md, docs/review/refine-l8/side-coast.png, docs/review/refine-l8/side-river.png, docs/review/refine-l8/side-pass.png, "planet/lineages/settlements.py::_ring_index", planet/lineages/trade_flow.py, planet/lineages/history/handover.py, "run 025b98 (split, scratch root l266/root, may be gone)", "run ebd83a (L7 baseline, scratch)", "world 5d09cc (899985 refined to L8, scratch)"]
created: 2026-11-10
updated: 2026-11-10
---

## In plain words
When the settled history runs on the finer L8 grid (the split, PW-1265), the town map gets better along rivers and passes
but worse on coasts: far fewer towns sit on the shore, most small islands have none, and there are a third as many cities.
If nothing is done, every L8 world reads as an inland, city-poor world, and anyone comparing L7 and L8 maps will trust a
difference that comes from the grid, not the world. Coordinator: this may be merged into PW-1627 (`intake --merge-into`).

## Description
Earth-like A (world 899985, dnd tree, seed 7), split run 025b98 on its L8 refine 5d09cc against the L7 run ebd83a on the
same code; both runs' towns read on the same fine world (`compare.py` in lane 267's scratch, numbers in
`docs/review/refine-l8/side-*.json`):
- towns and cities on the fine coast: L7 7.0%, split 1.9% (the coast is 7.5% of the fine land);
- islands under 0.3 Mkm2 with a town: 19 -> 6;
- villages / towns / cities: 21,440 / 6,494 / 331 (L7) -> 58,091 / 6,984 / 119 (split);
- the tech tree's town arms warn "the ledger still moved after 3 rounds" on the split run only.
Likely cause: the fixed ring counts PW-1627 lists (a town's footprint and pits, the coastal boat tier's two rings) and tier
thresholds that read heads per cell, so a quarter-area cell rarely reaches city size. Not tuned here (no thresholds moved).
- [ ] after PW-1627's km conversions, rerun the split on 5d09cc and compare coast share, islands with a town and cities to
      the L7 baseline (same code); explain what remains

## Updates
- 2026-11-10: Lane 270 rerun after PW-1627 and the refine's detail on the prolonged frames (split 727c35 on 69958b vs L7 2e0a95, same code; split.md §6): cities 244 vs 283, islands with a town 11 vs 21, on the fine coast 4.2% vs 7.3% (within ~60 km of the sea 8.8% vs 14.8%, the land's share 13.2%), rivers 34.6% vs 34.4%, none in the water. Cities fixed by the km rings; the coast fix took the coast from 1.9% to ~4%. Still open: towns under-sit the L8 coast and small islands by ~40%. First suspect to rule out: the harbour bonus that never fires (inbox draft-ledger-harbour-on-sea-cells.md).
- 2026-11-10: Created from inbox draft draft-l8-ledger-coast-cities.md (found by lane267b-pw1265).
- 2026-11-10: Lane 272c, after ladder.WATER_CELL_KM and RICH_KM (3d21c18b): split 393622 on 9cf1c3 vs L7 732ed6 (rerun 3413e1 identical), same code. On the fine coast 5.2% (old split f465d8 4.4%, L7 7.6%), within ~60 km 10.2% (9.1%, 15.2%), islands with a town 13 (11, 22), harbour towns 2.49% (1.97%, 3.39%). Partly closed; the rest is a coast-only shortfall (band towns ever 869 vs 1,384) likely the refine's soils; split.md 7.1, inbox draft draft-l8-coast-towns-remaining-gap.
