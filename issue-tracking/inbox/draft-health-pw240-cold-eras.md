---
title: "PW-240 update: health sweep cold eras: L6 seed 11 -384 m ice sea level (1 C) when its supercontinent drops to 4 plates; seeds 2, 77, 3199 to -205..-231 m"
type: task
status: todo
parent: null
subsystem: climate
effort: m
impact: high
found_by: health-sweep
blocked_by: []
relates: [PW-240, PW-191, PW-235, PW-264, PW-276]
refs: [docs/review/health/2026-10-15/report.md, tools/health.py]
---

## Description
Update for PW-240. PW-246 health sweep (2026-10-15, main 6926583, default params, 1 Gyr, keyframes
every 4 Myr; ice sea level = -0.9 x land ice volume / ocean area, as `earth.update_climate`):
| seed, level | worst ice sea level | keyframes < -150 m / < -250 m (of 238) | coldest global T |
|---|---|---|---|
| 11 L6 | -384 m @ 188 Myr | 17 / 13 | 1.0 C @ 180 |
| 77 L6 | -231 m @ 444 | 14 / 0 | 6.1 C @ 148 |
| 2 L6 | -223 m @ 608 | 21 / 0 | 3.5 C @ 496 |
| 3199 L6 | -205 m @ 480 | 17 / 0 | 9.5 C @ 504 |
| 505 L6 | -154 m @ 596 | 3 / 0 | 10.9 C |
| 1, 21, 42 L6 | -96..-131 m | 0 | 7.3-9.0 C |
| 3199 / 21 / 11 L7 | -108 / -125 / -137 m | 0 | 9.4 / 9.2 / 5.4 C |
So L7 stays inside the -150 m goal on all three seeds, and 4 of 8 L6 seeds dip below it for 3-9% of
the run; only seed 11 at L6 passes -250 m. Its cold era (164-216 Myr) is a supercontinent (largest
landmass 32-33% of the surface) whose plate count falls to 4-5 while the CO2 index drops to -1.1..-1.2
(the arc/ridge source collapsing with the plates): T 8.7 C at 144 Myr -> 2.2 C at 176 -> 1.0 C at 184,
ice 1.6% -> 13% of the surface, ice sea level -23 -> -384 m, recovering only slowly (-320 m at 216 Myr)
as plates return. Total sea level (with the ocean-basin term) reaches -548 m there. The L7 run of
seed 11 (9068cb, kept) has the same era colder than average but milder (5.4 C at 180 Myr, -137 m),
with 8+ plates throughout. The L6 runs were deleted; they reproduce from seed + 6926583.
- [ ] decide whether a few-plate supercontinent may glaciate this far (Earth's Cryogenian did, so a
  rare snowball-ish era may be acceptable) or whether the CO2 source should floor (volcanism not tied
  only to spreading and arcs)
