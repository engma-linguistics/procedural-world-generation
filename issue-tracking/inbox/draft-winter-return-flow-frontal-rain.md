---
title: "Winter subtropical east coasts: the return flow's vapour arrives but doesn't rain (no frontal / overrunning lift at low surface humidity)"
type: task
status: todo
parent: PW-013
milestone: v1
subsystem: climate
effort: l
impact: med
found_by: lane26
blocked_by: []
relates: [PW-998, PW-026]
refs: [planet/climate.py, docs/review/base-climate/coasts/README.md]
---

## Description
Split from PW-998 (lane 26, option b). **Mechanism:** winter rain on subtropical and mid-latitude east coasts is frontal.
Cyclones along the storm track lift the subtropical highs' return-flow air (Gulf, South China Sea, Kuroshio, Tasman)
over the cold dome. That rains at a low *surface* relative humidity. The kernel's large-scale rain runs at
(q/qs / rh_c)^3, so dryish surface air barely rains.

Numbers, Earth L6 (db7a178a -> lane 26 round 1, the shallow cold domes). Oct-Mar rain in mm/yr against GPCC; column
vapour in mm against NCEP:

| region | rain, main | rain, round 1 | GPCC | vapour, main | vapour, round 1 | NCEP |
|---|---|---|---|---|---|---|
| SE USA | 93 | 153 | 1334 | 3.7 | 7.7 | 17.5 |
| NE USA | 104 | 174 | 932 | 4.0 | 6.7 | 11.1 |
| SE China | 118 | 113 | 794 | 5.2 | 6.7 | 21.3 |
| E Australia (Apr-Sep) | 155 | 171 | 556 | 9.0 | | 15.0 |

- The winter wind on these coasts now has the right sign or nearly: SE USA v -1.6 -> +0.4 m/s, NCEP 925 hPa +1.2.
  The air's q/qs is 0.36, though, so the rain stays ~0.1x.
- 10x eddy mixing (lane 26 probe A) gives SE USA winter 199 at B 24.8, so mixing is not the lever.
- To do: design candidate forms of a storm-track lifting term (e.g. the large-scale rain's humidity gate relaxed by
  the storminess, or a rain term on the vapour's convergence across the baroclinic zone). Run one Earth solve each,
  and drop any form that doesn't move these regions. This is lane 26's round 2.
- Bar (with the Pampas jet ticket): SE USA and Pampas each at >= 60% of GPCC annual rain, B >= ~26, log-rain corr
  not below 0.69.
