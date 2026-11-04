---
id: PW-1230
title: In a +312 m highstand the continents rise with the sea (land stays ~34%), leaving vast lowlands within a few m of sea level
type: task
status: todo
parent: null
milestone: later
subsystem: tectonics
effort: s
impact: med
found_by: lane96
blocked_by: []
relates: [PW-051, PW-950, PW-238]
refs: [planet/tectonics/earth.py, planet/tectonics/crust.py, planet/surface.py, "run 2c0c5d", "world a16f5a", docs/review/l8-world/explore.md]
created: 2026-10-31
updated: 2026-11-03
---

## Description
In plain words: in the L8 world the sea rose 312 m in 100 Myr (young, fast-spreading oceans after the
supercontinent broke up), yet the share of land hardly changed, because the continents rose about as fast. Low
ground ends up piled just above the water: lots of land within a few metres of sea level, which Earth doesn't have
(and which makes the inland "sea puddles" of draft-below-sea-pockets-inside-land-count-as-sea). Worth a cheap
diagnosis: something may be lifting land to keep up with the sea when it should flood.

Run 2c0c5d (L8, seed 11), from its keyframes (lane 96, read-only):
| t (Myr) | sea level (m) | land % | continental crust elevation above the t=0 datum, p25 / p50 / p75 (m) | crust p50 (km) | sediment p50 (km) |
|---|---|---|---|---|---|
| 0 | 0 | 31.8 | 111 / 350 / 705 | 35.0 | 0.30 |
| 64 | 168 | 34.5 | 262 / 431 / 738 | 35.0 | 0.50 |
| 100 | 312 | 33.9 | 365 / 511 / 801 | 36.0 | 0.60 |
("Above the datum" = keyframe elevation + the frame's sea level.) The lower quartile rose ~250 m while the
sea rose 312 m. Thicker crust (+1 km, ~150 m at 150 m/km: the crust thermostat holding volume while area fell
40.0 -> 39.3%) and sediment (+0.3 km) look like most of it, but the coincidence with the sea's rise is suspicious.
Result in world a16f5a: 6.3% of land is 0-10 m and 17.8% is 0-50 m (Earth ETOPO1 resampled to the L8 grid:
1.4% and 6.7%; L7 2a7385: 1.9% and 7.2%); 49% of land is below 200 m (Earth on L8: 27%). Ocean floor mean age
26.7 Myr (2a7385: 55.7), sea_tect +324 m against the +-400 m limiter (PW-051's young-ocean side).

Check: (1) what lifts the lower quartile frame by frame (thermostat arc growth landing on low continent?
sediment filling flooded platforms to -60 m and deltas to +2 m? the weathering base level riding the sea?);
(2) whether a Cretaceous-style highstand floods more land than this anywhere in the L6 multi-seed set.
Not a resolution effect as far as I can tell; same code at L7 should show it after a breakup.

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: second-order tectonics refinement; the planet is stable without it
- 2026-10-31: Created from inbox draft draft-continents-rise-with-the-sea-in-a-highstand.md (found by lane96).
