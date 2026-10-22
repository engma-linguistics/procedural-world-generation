---
title: Earth Köppen group 70% against main's 71% after PW-578; the gap is stage 2b's temperatures (D→E, A→C), not the rain
type: task
status: todo
parent: null
subsystem: climate
effort: m
impact: med
found_by: laneA4 (PW-578 attempt 2)
blocked_by: []
relates: [PW-578, PW-346, PW-577]
refs: [planet/climate.py, docs/review/base-climate/pw578/earth_check_after.txt, docs/review/base-climate/stage2b/ec_main.txt]
---

## Description
With PW-578 attempt 2, Earth L6 log-rain r is 0.619 (main 0.617), but the Köppen main group is 69.6% (main 71%).
The control proves this isn't the rain: the branch with main's uniform 6 C × s sea swing everywhere scores group
70.2.

Confusion rows against main: obs D → model E 14% (main 11%); obs A → A 78% (80); obs B → B 47% (48). The D→E
cells are cold coasts whose summers are too cool. The near-land seas at 50–65N have summers 1.7–3.5 C too cold
against NCEP (`seaswing` bins, land_air > 0.3) and winters ~4 C too cold. Stage 2b's freezing deficit
(`_summer_half`) and the sea air equal to the water in summer both pull them down.

One idea tried and dropped: letting the summer land air keep its warmth over the sea (a stable carry over
air_km_w). It warmed the 35–65N near-land seas 1.5–3.8 C too much.
- [ ] find why the high-latitude near-land seas' summer air is too cold, without the overshoot
