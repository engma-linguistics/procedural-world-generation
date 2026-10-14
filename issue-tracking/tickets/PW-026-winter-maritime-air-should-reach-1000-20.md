---
id: PW-026
title: Winter maritime air should reach 1000-2000 km inland under westerlies
type: task
status: todo
parent: null
subsystem: climate
effort: m
impact: high
found_by: ocean
blocked_by: []
relates: [PW-022]
refs: [planet/climate.py, tools/earth_check.py, "world 2f38e3", "plan_next@bdc967f: Known issues → Climate"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Western Europe's winters are ~4.8 °C too cold (−4.2 °C against 0.6 observed) and Scandinavia's coldest
month is −22.3 °C against −8.2 (NCEP). The overturning fixed most of the sea (Norway's coast SST 0.9 →
~5–6 °C, observed ~7.5), and even a sea 8 °C warmer all over the NE Atlantic only brings W Europe to
−3 °C. So the cause is the air model: maritime air should reach 1000–2000 km inland in winter under the
westerlies (and the reverse on east coasts). Also check the old continental-winter errors (Siberia,
Alaska, Quebec, NE China 5–10 °C off) with the same change.

## Updates
- 2026-10-14: Created from the owner discussion 2026-10-14 (air model, not ocean). Merged Known issues 'Norway too cold' (ocean), 'Older Earth errors: winters 5–10 °C off' (v1), morning decision 3(d).
