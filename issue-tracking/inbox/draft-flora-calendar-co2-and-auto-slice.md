---
title: "Plant calendar (PW-807) consequences: bare-land spin-up against the CO2 reference freeze, and slice --at auto's flora gate leaving only the last ~10-30 Myr"
type: task
status: todo
parent: PW-244
milestone: v1
subsystem: climate
effort: m
impact: high
found_by: star-anchor-audit
blocked_by: []
relates: [PW-807, PW-636, PW-634, PW-700, PW-798]
refs: [planet/vegetation.py, planet/tectonics/earth.py, planet/highlights.py, planet/make.py, tests/test_vegetation.py, docs/review/base-climate/star-anchor-audit/]
---

## Description
Audit items 6 and 7 (docs/review/base-climate/star-anchor-audit/README.md).

The compression to remove: `FLORA_PACE` 0.8, the `GROUPS` fractions of ~470 Myr, and `group_windows`' deadline
D = end - max(16 Myr, 5%) (planet/vegetation.py:222-286). Also `plants_from` 0, `FLORA_END` 1000, and
test_vegetation's group_windows test.

Knock-ons to measure:
- **CO2.** A run longer than ~470 Myr gets bare continents first: the weathering `plants` factor is 1.0 against up to
  1.75, and bare ground erodes up to 1.6x faster. On runs over ~770 Myr the reference freezes at 300 Myr on bare
  land, and the plants' arrival is then a lasting weathering surplus (cooling). The direction is physical (the
  Devonian drawdown), but its size on top of the anchored star's dim start is unmeasured. Measure it with the star
  zero-point decision. PW-798 A's "freeze once the start has settled" may need "once land plants exist".
- **`--at auto`.** `highlights.representative_time` restricts to frames after the last group. On the real calendar
  that is ~30-8 Ma, which leaves 2-7 keyframes. The geographic-typicality medians and PW-700's warm-moment-of-the-era
  pick then mostly degenerate to the last frame. Owner question already in PW-807. One option: gate on flowering
  trees (~100 Ma) or grasses (~55 Ma), not C4 grasses.
- [ ] CO2 reference vs plant arrival measured on a 1 Gyr L6 run
- [ ] --at auto rule decided and test_highlights updated
