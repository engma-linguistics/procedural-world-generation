---
title: The summer land-sea inflow carries the whole column's vapour past the coast and rains it 1000-2500 km inland (40-50 N too wet, monsoon coasts too dry)
type: task
status: todo
parent: PW-015
milestone: v1
subsystem: climate
effort: m
impact: high
found_by: lane58
blocked_by: []
relates: [PW-1093, PW-1097, PW-1094, PW-026]
refs: [planet/climate.py, tools/moisture_regions.py, docs/review/base-climate/moisture-budget/README.md]
---

## Description
In plain words. In summer the model's continents draw sea air in across their coasts, as real ones do. But that
inflow is too strong, it carries all the air's vapour (not just the low layer's), and nothing makes it rain where it
comes ashore. So the vapour blows past the coast and rains far inland. This one flow is why Mongolia, the Great
Plains, NE USA and the Sahel are too wet. It is also the only thing keeping the US south-east, the Pampas, India and
SE China as wet as they are. Turn it down and both ends move together.

Measured (lane 58, Earth L6 on 347b4374; README section 3):
- `monsoon_wind` makes the land-sea wind poleward of 15 deg as 0.9 x geostrophic - 0.45 x the pressure gradient.
  The second term is the cross-isobar inflow. The vapour rides all of it (`face_winds`).
- Whole-Earth solves with the 0.45 at 0.45 / 0.3 / 0.2 / 0 (`tools/moisture_regions.py --ageo`):

  | | obs | 0.45 | 0.3 | 0.2 | 0 |
  |---|---|---|---|---|---|
  | land 40-50 N | 537 | 952 | 884 | 817 | 668 |
  | Gobi/Mongolia | 157 | 601 | 432 | 284 | 117 |
  | Great Plains | 550 | 896 | 589 | 428 | 272 |
  | SE USA | 1328 | 636 | 451 | 382 | 319 |
  | Pampas | 944 | 401 | 234 | 190 | 168 |

  B goes 25.2 -> 28.5 -> 31.5 (Kottek 30.1), exact 38 -> 40 -> 41, corr 0.721 -> 0.702 -> 0.681. India goes
  632 -> 445 -> 364 (GPCC 1111).
- Gulf inflow path, Apr-Sep (`moisture_budget` inland paths): the model rains 0.22x the observed rate in the first 250 km
  and 2.0-2.8x at 1250-2250 km.
- Lane 26 measured the summer onshore wind at SE USA +5.0 and Japan +5.4 m/s, against NCEP +1.1-1.6.
- Lane 25's PW-015 round 2 (the vapour's share of the land-sea circulation) hit the same trade-off: B 26-31, corr
  0.58-0.62, India drier.

What to do: one design round pairing two soundness changes, probed on Earth one solve per form:
- (a) the inflow carries only its boundary layer's share of the column's vapour;
- (b) the large-scale rain responds to the wind's low-level convergence (see the draft on the missing convergence
  lift), so the inflow rains where it comes ashore.

Don't just lower the 0.45: that's a retune, and it trades the interiors for the coasts.
- [ ] land 40-50 N toward GPCC (now 1.8x), B not below 25, corr not below 0.70, SE USA and Pampas not below main
