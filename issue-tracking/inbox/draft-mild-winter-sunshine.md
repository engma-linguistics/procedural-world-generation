---
title: "Travel: mild-winter retreats still use a dry winter month as the sunshine proxy"
type: task
status: todo
parent: null
subsystem: highlights
effort: xs
impact: low
found_by: clouds
blocked_by: []
relates: [PW-142, PW-143]
refs: [planet/highlights.py]
---

## Description
The beach finder now uses the summer's sunshine hours (sunshine_jul / sunshine_jan, PW-143),
but the mild-winter retreat finder (`highlights.mild_winters`, MILD_MAX_RAIN = 70 mm in the
winter month) still uses a dry winter month as its stand-in for "sunny". A winter sun retreat
(the Canaries, the Algarve, Florida) is about sunshine: gate it on the winter half-year's
sunshine (e.g. >= 5-6 h/day; the Canaries ~6-7, Nice ~5, London ~2) and put the hours in the
blurb, as the beaches do ("January 16 °C, 6 h of sunshine a day, 17 mm of rain").
- [ ] mild winters ranked by winter sunshine; test_highlights updated
