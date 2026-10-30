---
title: "Rich land where nobody lives holds far fewer dragons than its food would feed (1.9 vs 36.9 per 1,000 km2): thin visitors' pressure or absence, not measured"
type: task
status: todo
parent: null
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: dragon-density-doc
blocked_by: []
relates: [PW-977, PW-990]
refs: [docs/review/megafauna/dragon-density/index.html, docs/review/megafauna/dragon-density/numbers.json, planet/lineages/history/megafauna.py]
---

## Description
**In plain words.** On empty land, the richer the grazing the more dragons it should hold. In one run that holds up to about 2.5 tonnes of grazers per km², then breaks: the richest empty land has fewer dragons than middling land, about a twentieth of what its food would feed.

World 2a7385 roll 7000, the present (`numbers.json` `cells_2a7385.0.by_class.none`): poor empty land (0.14 t/km² of prey) holds 0.35
dragons per 1,000 km² against 0.86 the food would feed; middling (1.73 t/km²) 6.8 against 10.5; rich (6.05 t/km², only 190 cells)
1.9 against 36.9. The 25 kyr era shows the same (rich 6.8 against 36.5).

Likely causes, not yet measured:
1. "Nobody's country" on the page means under 0.02 people/km². `megafauna.pressure` already bites there: at 0.02/km² it is 0.33,
   which presses a 1-per-26 km² natural density to about 0.18 of itself (geometric toward meta.dragon_km2).
2. No dragon kind holds those cells (presence 0), since rich land sits next to peopled country.
- [ ] split the gap into pressure and absence (presence-weighted vs not) on the saved ERAS.npz
- [ ] if (1), it is stage 3's to fix (softer pressure); if (2), check scatter's reach into rich empty land
