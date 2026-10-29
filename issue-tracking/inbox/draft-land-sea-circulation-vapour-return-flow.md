---
title: "The vapour rides the whole land-sea (monsoon) circulation with no return flow aloft, so land imports ~2x the vapour it should (runoff/rain 0.49 vs 0.38; the Sahel, Australia and S Africa rain 3-11x GPCC in summer)"
type: task
status: todo
parent: PW-013
milestone: v2
subsystem: climate
effort: l
impact: high
found_by: lane25
blocked_by: []
relates: [PW-015, PW-228, PW-233]
refs: [planet/climate.py, tools/earth_check.py, tools/moisture_budget.py, docs/review/base-climate/deserts/README.md]
---

## Description
Lane 25's diagnosis of the Earth Koppen-B deficit (docs/review/base-climate/deserts/README.md). The B land the model
misses is warm-season land rain at the monsoons' margins: Sahel/W Africa 3.4% of land, Australia 2.2, S Africa 1.6,
Mongolia 1.2, W North America 1.3, C Asia 1.0, E Africa 0.9; summer rain there runs 3-11x GPCC with the vapour (PW) near
observed. It is supply-limited: halving the showers' ITCZ boost, or the showers' rate under the sinking air, leaves the
Sahel within 5%. What sets it is how much vapour the wind brings in.

In `compute`, the vapour rides the full surface wind (`vq_jul/jan`), including `monsoon_wind`'s land-sea part. That
circulation is a closed cell: a shallow heat low or winter high has its return flow at 2-4 km, where the vapour is
e^(-h/H) thinner. For a cell of depth h with the return flow above it, the net vapour flux is (1 - e^(-h/H))^2 of the
column's (H ~2 km: 0.28 at 1.5 km, 0.60 at 3 km). A deep convective monsoon (India, East Asia) returns near the
tropopause and imports nearly all of it.

Measured (Earth L6, main, the vapour's share s of the land-sea part; temperatures' winds unchanged):
- s = 0.5: B 20 -> 28%, exact 34 -> 38%, land rain 1122 -> 969 mm (GPCC 791), Sahel 2427 -> 1770, Australia interior
  751 -> 230, Gobi 585 -> 221. But log-rain corr 0.648 -> 0.621, India 696 -> 505 (GPCC 1109), SE USA 1109 -> 570.
- s = 0.3 plus deepening from a first pass's rain (s up to 1 at >= 2000-4000 mm/yr): B 29-30%, corr 0.58, India 428-445.
  A rain-based depth punishes India, which is already too dry.

So the mechanism is real and strong, but it needs a sound depth for each cell's circulation: dry heat lows and winter
highs shallow (`low_column`'s depths are a start), deep where moist convection heats the column. The discriminator
can't be the model's own rain (it is wet everywhere at the margins). Something like the inflow's convective potential
(the inflow air's moist static energy against the tropics' reference aloft) might do. Measure with
`tools/earth_check.py`, `tools/moisture_budget.py` (inland paths) and the paired judge
(docs/review/base-climate/v1-finish-16/pjudge.py).
- [ ] Earth B within ~3 points of 30% with log-rain corr not below main's, India not drier
