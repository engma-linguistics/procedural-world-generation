---
id: PW-026
title: Winter maritime air should reach 1000-2000 km inland under westerlies
type: task
status: todo
parent: null
milestone: v2
subsystem: climate
effort: m
impact: high
found_by: ocean
blocked_by: []
relates: [PW-022]
refs: [planet/climate.py, tools/earth_check.py, "plan_next@bdc967f: Known issues → Climate"]
created: 2026-10-14
updated: 2026-10-30
---

## Description
Western Europe's winters are ~4.8 °C too cold (−4.2 °C against 0.6 observed) and Scandinavia's coldest
month is −22.3 °C against −8.2 (NCEP). The overturning fixed most of the sea (Norway's coast SST 0.9 →
~5–6 °C, observed ~7.5), and even a sea 8 °C warmer all over the NE Atlantic only brings W Europe to
−3 °C. So the cause is the air model: maritime air should reach 1000–2000 km inland in winter under the
westerlies (and the reverse on east coasts). Also check the old continental-winter errors (Siberia,
Alaska, Quebec, NE China 5–10 °C off) with the same change.

## Updates
- 2026-10-30: Owner 10-30 D11: moisture/monsoon-coast work parked for v2; an agent will find a downloadable drag source.
- 2026-10-30: Lane 58 (docs/review/base-climate/moisture-budget/README.md): the winter westerlies bring ~3x the observed net vapour into Europe and Russia
  (W Europe +1345 vs +411, European Russia +962 vs +284, W Siberia +518 vs +168 mm/yr), and it rains as
  oversaturation inland (51-62%). The excess is the import across the coast, not the speed inland: a 0.7x winter
  land wind piles the vapour at the coast (W Europe +130).
- 2026-10-29: Lane 26, Earth L6 on db7a178a, coldest month model / NCEP: W Europe -0.6 / 0.7, Scandinavia (58-70N, 5-30E) -8.5 / -8.2, so the description's -4.2 and -22.3 are out of date. Still off: Alaska -29.1 / -19.0, NE China -9.2 / -17.9, Japan 8.6 / 2.0, Quebec -16.2 / -20.2.
- 2026-10-29: Pulled into v1 (owner 10-29) with PW-998: the sea's bulk exchange exposed that maritime air doesn't reach far enough inland (SE USA, Japan, Pampas dry).
- 2026-10-14: Created from the owner discussion 2026-10-14 (air model, not ocean). Merged Known issues 'Norway too cold' (ocean), 'Older Earth errors: winters 5–10 °C off' (v1), morning decision 3(d).
