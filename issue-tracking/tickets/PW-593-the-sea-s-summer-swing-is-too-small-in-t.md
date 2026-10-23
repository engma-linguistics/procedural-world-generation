---
id: PW-593
title: "The sea's summer swing is too small in the NH (NE Atlantic 1.7 vs 3.2 C, Norwegian Sea 1.8 vs 4.0, NE Pacific 2.0 vs 3.9) and too big off SH coasts: one 50 m layer for every summer, whatever the wind"
type: task
status: todo
parent: PW-470
milestone: v1
subsystem: ocean
effort: m
impact: high
found_by: base-climate-laneA13
blocked_by: []
relates: [PW-589, PW-580, PW-573]
refs: [planet/climate.py, docs/review/base-climate/laneA13/bands_fold.txt, docs/review/base-climate/stages.md]
created: 2026-10-22
updated: 2026-10-22
---

## Description
After PW-589 (lane A13, the overturning's heat folded over both hemispheres), the near-land annual sea air is
within ±2 C on most rows. W Europe's warmest month is still −1.2 C (bar: +0.4, before stage 3), because what is left
is the sea's summer swing, not its annual mean.

Earth L6, sea cells, half the range of the monthly air (model / NCEP; `laneA13/bands_fold.txt`):

| box | half-swing | warmest month | coldest month |
|---|---|---|---|
| NE Atlantic 45–55N | 1.7 / 3.2 | 15.4 / 16.5 | 11.9 / 10.1 |
| Norwegian Sea 60–70N | 1.8 / 4.0 | 10.9 / 11.5 | 7.4 / 3.5 |
| NE Pacific 40–50N | 2.0 / 3.9 | 12.2 / 16.3 | 8.1 / 8.5 |
| Gulf of Alaska | 3.7 / 4.9 | 8.5 / 12.6 | 1.0 / 2.9 |
| S Atlantic off Patagonia | 6.2 / 3.7 | 17.5 / 14.5 | 5.2 / 7.0 |
| Tasman | 3.7 / 2.7 | 22.8 / 18.2 | 15.3 / 12.7 |

- In the NH the warmest month is too cold and the coldest too warm: the swing is too small, with the mean about right.
- Off the SH coasts it is the other way round.
- By band, the NH near-land warmest month is still 1.5–4.2 C too cold at 35–60N; the SH's is 1.7–3.7 C too warm
  at 35–60S.

Likely mechanism: `_sea_half`'s own swing puts the summer's sunshine into one `brine_m` (50 m) layer everywhere. The
real summer layer is set by the wind's stirring against the summer's heating (Monin–Obukhov / Kraus–Turner, depth
~ u*^3 / B). It is ~20–30 m under the NH's weak summer winds and 50–80 m under the SH's summer westerlies. That is
one physical rule that gives both hemispheres' errors their sign.

Not done in lane A13: the depth goes as U^3, so it needs its own measurement pass (rain r, the time zoom's endings
test, the lakes).
- [ ] the summer's mixed layer from the summer wind (and the summer heating), not a fixed 50 m
- [ ] W Europe's warmest month no worse than +0.4; NE Atlantic / NE Pacific summer sea air within 2 C

## Updates
- 2026-10-22: Created from inbox draft draft-sea-summer-swing-wind-mixed-layer.md (found by base-climate-laneA13).
