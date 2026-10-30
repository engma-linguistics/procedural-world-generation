---
id: PW-1099
title: The summer land-sea inflow carries the whole column's vapour past the coast and rains it 1000-2500 km inland (40-50 N too wet, monsoon coasts too dry)
type: task
status: todo
parent: PW-015
milestone: v2
subsystem: climate
effort: m
impact: high
found_by: lane58
blocked_by: []
relates: [PW-1093, PW-1097, PW-1094, PW-026]
refs: [planet/climate.py, docs/review/base-climate/moisture-inflow-ascent/, tools/moisture_regions.py, docs/review/base-climate/moisture-budget/README.md]
created: 2026-10-30
updated: 2026-10-30
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

## Updates
- 2026-10-30: Owner 10-30 D11: moisture/monsoon-coast work parked for v2; an agent will find a downloadable drag source.
- 2026-10-30: Lane 62 round 2 (partner probe, not committed). In plain words: adding lift where the air rises can't
  be the partner, because the coasts lack vapour, not lift. A western-flank ascent from the planet's spin (the
  model's along-isobar wind has no 1/f, so it never converges; real flow does, div = -(cot(lat)/a) v) moves SE USA
  318 -> 320-334 with the inflow depth on (main 636), the Pampas 171 -> 172-190, r 0.665-0.668. The SE USA summer box
  loses vapour (PW 25 -> 18 mm, NCEP 33.5) and its land evaporation (717 -> 215). The partner needs a supply: draft
  on the monsoon coasts' vapour supply (friction contrast, moister source seas, the land's vapour residence).
- 2026-10-30: Lane 62 round 1 (whole-Earth solves L6/L7; numbers in PW-1100's update too). In plain words: making
  the inflow carry only its low layer's vapour dries the interiors as hoped, but it also takes away most of the
  monsoon coasts' rain, and nothing in this round gives it back. The coasts' rain in the model rests on the
  inflow's whole-column vapour. The code is kept as a patch, not merged (coordinator: option b, no judge):
  docs/review/base-climate/moisture-inflow-ascent/ (TUNE inflow_bl, climate.inflow_share).
  - Form: the cross-isobar part of monsoon_wind (now its third return) carries f = 1 - exp(-h q_k LAPSE) of the
    vapour. That is the share of a column whose vapour e-folds over 1 / (q_k LAPSE) = 2.56 km (the model's own
    constants, fixed relative humidity), below the friction layer h. h is sea_bl_m 500 m at sea (f 0.18), sum_h
    1500 m on summer land (0.44), air_m 1000 m on winter land (0.32). No new parameters.
  - L6, obs / main / inflow depth / + ascent (B2) / uniform 1500 m + ascent: land 40-50N 537 / 952 / 775 / 772 /
    793; Mongolia 157 / 601 / 250 / 251 / 250; Great Plains 550 / 896 / 411 / 413 / 420; NE USA 1032 / 1490 /
    902 / 907 / 1143; SE USA 1328 / 636 / 318 / 319 / 417 (Apr-Sep 1323 / 912 / 210 / 213 / 428); Pampas 944 /
    401 / 171 / 178 / 200; India 1111 / 632 / 338 / 339 / 382; SE China 1462 / 1052 / 499 / 499 / 730; Sahel 593
    / 2099 / 1534 / 1518 / 1520. B 25.2 / 33.3 / 32.6 / 31.4 (Kottek 30.1), exact 38.4 / 41.4 / 41.0 / 40.9,
    log-rain r 0.721 / 0.666 / 0.662 / 0.673. L7 within a few % (main r 0.717, inflow depth 0.665). Fails the bar
    on SE USA, the Pampas and r.
  - Why the coasts fall: the SE USA summer wind (L6 box mean) is poleward +3.5 m/s along the isobars plus +1.3
    cross-isobar. Removing 56-82% of only the cross-isobar part's vapour cuts the summer rain by 50-75%. So the
    along-isobar flow doesn't bring the Gulf's vapour onto the coast in the model; the inflow does.
  - The convergence-lift partner (PW-1100) doesn't rain the inflow at the coast. The model's land-sea wind has no
    friction contrast at the coastline, so its convergence peaks at the heat lows' centres (Mongolia, Sahel), not
    where the air comes ashore.
  - Next (coordinator 10-30): design the partner that gives the coasts their vapour from a sound source (the
    highs' western-flank return flow / low-level jets, PW-1094 / PW-1097 / lane 58's fix D; or a land-sea friction
    contrast), with the same Earth gate, before inflow_bl can merge.
- 2026-10-30: Created from inbox draft draft-land-sea-inflow-overshoots-inland.md (found by lane58).
