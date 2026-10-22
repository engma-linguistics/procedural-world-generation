---
title: "Small lands get a big continent's seasons: Southern Hemisphere coasts' seasonal range 16.5 vs 9.6 C, summers +4-6 C (Patagonia +6.4)"
type: task
status: todo
parent: null
milestone: v2
subsystem: climate
effort: m
impact: med
found_by: base-climate-review
blocked_by: []
relates: [PW-352, PW-026]
refs: [planet/climate.py, tools/climate_bias.py, docs/review/base-climate-review.md]
---

## Description
**Measured** on Earth L6 (`tools/climate_bias.py`, section 2): the seasonal range (warmest minus coldest month) of
ice-free land poleward of 35 deg, by distance from the sea, model against NCEP.

| distance from the sea | north | south |
|---|---|---|
| at the coast | 27.5 / 26.4 | 16.5 / 9.6 |
| 150–400 km | 33.3 / 30.8 | 22.2 / 14.1 |
| 400–800 km | | 23.7 / 17.6 |
| 800–1500 km | 34.7 / 34.7 | |

- The scheme fits the north.
- In the south, summers are 4–6 C too warm at every rain level (Patagonia +6.4, Hobart +7.5).

**Why.** The land's own swing (`continental` 24 C × the season strength) doesn't depend on how big the land is. So a
400 km-wide land in the westerlies keeps "its own" continental air.

**Why it matters.** On made-up worlds with islands and narrow continents it overstates the seasons. For ice it gives
the margins hot summers.

**What to try.** Make the land's own swing proportional to the land upwind within a continent's scale (~1000–2000 km),
together with PW-352's energy split.

- [ ] the SH coastal seasonal range within 1.3× NCEP's; the NH continentality rows within 2 C of now
