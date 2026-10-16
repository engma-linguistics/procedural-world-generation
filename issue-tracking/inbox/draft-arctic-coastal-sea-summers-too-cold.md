---
title: "Climate: Arctic coastal seas' summers ~4 C too cold, so the Laptev and Kara coasts never thaw (no waves, too much sea ice)"
type: task
status: todo
parent: null
subsystem: climate
effort: m
impact: low
found_by: coast-batch
blocked_by: []
relates: [PW-230, PW-112]
refs: [planet/climate.py, planet/coast.py, tools/coast_check.py]
---

## Description
On the Earth world (L6, the model's coupled climate as tools/coast_check.py builds it), the warmest month over the 239 coastal sea cells between 66 and 78 N has a median of -1.2 C, against 2.7 C observed (`obs_t_warm` in tools/earth_data.py). 47% of them stay below climate.FREEZE (-1.8 C) all year, so coast.sea_ice_share calls them frozen in both half-years. The Laptev coast cell off the Lena delta (cell 24686) is at -2.1 C (observed 4.9 C), the Kara cell off the Ob/Yenisei gulfs (20350) at -3.1 C (observed 2.5 C). Their land neighbours are at +4..+7 C, so it's the sea cells that are too cold: sst_jul there is -1.2 C, pinned near freezing.

Because of this, coast_check's Laptev and Kara wave rows stay at 0.0 kW/m (observed 0.3-3) after PW-230. PW-230 replaced the wave rays' hard ice block (a ray stopped wherever a half-year was at least half frozen) with an integral over the coast's open season. As a diagnostic, +3 C on the Arctic sea cells' warmest month gives Laptev 5.4 and Kara 4.5 kW/m (open 52% / 40% of the July half-year), so the coast side is ready once the climate thaws them. The same cold bias over-ices those seas for coastal life (kelp and seagrass ice gates) and for the tides' ice friction.

What to look at: the summer sea surface over shallow Arctic shelves next to big rivers (warm river water and the shallow mixed layer warm them to +2..+8 C in August), and whether the sea cells' warm month is held near freezing by the model's sea ice or by the ocean's mixed layer. Fix in the climate, not by lowering coast's freeze threshold.
- [ ] Arctic coastal sea cells' warmest month within ~1.5 C of observed (median)
- [ ] coast_check Laptev and Kara waves above 0 (0.3-3 kW/m observed)
