---
id: PW-633
title: "The sea's seasonal layer is 50 m everywhere, also on shelves shallower than that (North Sea, Baltic, Yellow Sea: ~40% of their L6 cells): a shelf sea should swing as its whole column. On step 2 of PW-627 it can't yet help, because those seas' annual SST is ~3 C too cold (PW-592) and the bigger winter half freezes them"
type: task
status: todo
parent: PW-470
milestone: v1
subsystem: ocean
effort: s
impact: med
found_by: base-climate-laneA18
blocked_by: []
relates: [PW-627, PW-592, PW-593, PW-595]
refs: [planet/climate.py, docs/review/base-climate/laneA18/step2_shelf_probe.diff, docs/review/base-climate/laneA18/depth.py, docs/review/base-climate/laneA18/seabox.py, docs/review/base-climate/stages.md]
created: 2026-10-23
updated: 2026-10-23
---

## Description
`_sea_half` puts the seasons' heat into a `brine_m` = 50 m layer on every sea cell. Where the sea floor is
shallower, the whole column is the layer (tidal shelf seas are mixed to the bottom), so the heat capacity is the
depth's, not 50 m's. The physics is plain and needs no constant: `min(brine_m, depth)`.

It is the one summer-layer mechanism lane A18 found that is independent of the winds and differs by hemisphere for
a geographic reason (`laneA18/depth.py`, Earth L6, ocean cells 20-65 deg):
- shallower than 50 m: N 4.1%, S 0.4%; shallower than 100 m: N 7.6%, S 1.0%;
- North Sea 45% of cells under 50 m (median 62 m), Baltic 44%, Yellow / East China Sea 39%; Patagonian shelf 6%
  (median 117 m), Tasman, Agulhas and NE Atlantic 0%.

Tried on PW-627's step 2 (`laneA18/step2_shelf_probe.diff`, toggle `shelf_probe`): the North Sea's halves go from
3.7 / 7.1 to 7.1 / 11.0 C (summer / winter), but its sea air's swing stays 4.3 (obs 5.9), and the bars barely move
(rain r 0.649 -> 0.653, Biscay-N Sea warmest -5.4 -> -5.3, near-land N swing within 1.5x 33 -> 35%, SH unchanged).
The reason: the North Sea's annual SST is 6.8 C against ~10.5 observed (PW-592's "the inflow's heat doesn't reach the
marginal seas": moc heat +1.4 there vs +3.6 in the NE Atlantic, Biscay -0.2), so the bigger winter half takes the
water below freezing, and `_summer_half` spends the summer's gain on melting that ice. The winter half is also too
big because the land part gives the air off Britain a continent's swing (PW-595).

So: land it after (or with) PW-592's inflow into the marginal seas and PW-595's land part by the land's width; then
re-measure. Stage 1 to check: sea ice on shallow shelves grows with it (the Siberian shelves, Hudson Bay, the Bohai),
which is right, but the overturning's sites and the Norwegian coast need the usual bars.
- [ ] the seasons' layer no deeper than the sea floor, with the Earth bars and stage 1 measured after PW-592

## Updates
- 2026-10-23: Lane A20: with the shelf-air rule + step 2, the shelf-depth layer moves W Europe warmest -1.6 -> -1.3.
- 2026-10-23: Created from inbox draft draft-sea-layer-deeper-than-shelf.md (found by base-climate-laneA18).
