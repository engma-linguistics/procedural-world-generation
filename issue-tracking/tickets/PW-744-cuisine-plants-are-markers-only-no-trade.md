---
id: PW-744
title: "Cuisine plants are markers only: no trade goods, no ferments, crude wild ranges for tea, spice and capsicum"
type: task
status: todo
parent: PW-692
milestone: later
subsystem: food
effort: m
impact: low
found_by: fun9
blocked_by: []
relates: [PW-738, PW-721, PW-719]
refs: [planet/lineages/crop_defs.py, planet/lineages/crops.py]
created: 2026-10-24
updated: 2026-11-03
---

## Description
PW-738 added twelve rows (tree fruit and nuts, olives, vines, oil seeds, coconut and oil palm, tropical spices, chili-like capsicum, cane, sap sugar,
tea and coffee, greens, alliums) with weight 0 and small `k`. What is left:
- the wild ranges are climate windows only (olive and vine read the Mediterranean Koppen classes); spice trees and tea ignore canopy shade and
  altitude terraces; capsicum has no link to the senses epic (`body.capsaicin`: a bird people feels none) beyond the brief;
- nothing carries the plants as trade goods (oil, wine, sugar and spices travel; a region without them wants them): needs the trade pass;
- ferments (wine, cane spirits, rice beer) follow the plants known but the brief's `drink` stays null;
- the crop layers are uint32 now (24 rows); 32 is the next ceiling.
- [ ] wild ranges checked against the world's own soils and shade; trade and ferment hooks

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: culinary follow-up of low weight; the core brief and cuisine tickets stay in v2
- 2026-10-26: Milestone v3 -> v2. (PW-900 backlog reorg).
- 2026-10-24: Created from inbox draft draft-cuisine-plants-effects-and-trade.md (found by fun9).
