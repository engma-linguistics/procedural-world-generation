---
title: "Tibet's summer rain is a quarter of GPCC's (141 vs 531 mm/yr): the monsoon's vapour never climbs onto the plateau"
type: task
status: todo
parent: PW-013
subsystem: climate
effort: m
impact: low
found_by: moisture-budget
blocked_by: []
relates: [PW-015, PW-233]
refs: [planet/climate.py, tools/moisture_budget.py, docs/review/moisture-budget-2026-10-16/earth_L6.md]
---

## Description
tools/moisture_budget.py, Earth L6, Tibet box (30-36N, 80-95E), Apr-Sep:
- P is 141 mm/yr (half-year rate) vs GPCC 531; earth_check gives 76 vs 296 annual. The plateau is the one interior that is too dry.
- PW is 4.9 vs NCEP 6.4 mm. The vapour is 0.77 of NCEP, but it rains at 0.35 of the observed efficiency: showers make 87% of the rain, and the trigger is barely positive (dry part -4.0 C, LQ q 4.9 C).
- At L7 it is drier still (54 mm). In every PW-015 prototype variant Tibet falls further (9-70 mm), because each one curbs the showers.

Likely causes:
- `deflect` turns the low-level wind along slopes above 1500 m, so the monsoon air goes round the plateau, not up it. Real moisture reaches it through the SE valleys and in upslope convection.
- The kernel's capacity over high ground cools by only lapse_q = 0.5 of the lapse rate, so q/qs comes out at 0.24.

What to try:
- let part of the column's vapour cross blocked terrain (the vapour sits above the blocked layer, like PW-332's polar drift);
- give the elevated heat source its share of the trigger (the plateau's air aloft is warmer than the latitude's).
- [ ] Tibet Apr-Sep P within 2x of GPCC, with the Himalayan front and the Gobi not wetter
