---
id: PW-434
title: Cold eras' sea levels deepen after PW-366's thicker run sheets (worst -368..-609 m, 3 of 4 seeds past -430)
type: task
status: needs-decision
parent: null
subsystem: climate
effort: m
impact: high
found_by: pw366
blocked_by: []
relates: [PW-240, PW-366, PW-364, PW-421]
refs: [planet/icemass.py, planet/tectonics/earth.py, tools/sealevel.py]
created: 2026-10-19
updated: 2026-10-19
---

## Description
PW-366 made the run's sheets 75 kPa Nye profiles with each cell's mean rise (and margins at the edge's
balance). The same extent now holds about 2x the ice at L6 (L6 seed 2 @ 580 Myr: 133 Mkm3 / 11.4% of the
surface at dT -5.9, sea level -593 m; the old code's run had 62 Mkm3 / 8.5% at dT -2.6, -292 m), and the
deeper ice cools the planet further through the ice albedo. L6, 1 Gyr, `tools/sealevel.py`, sea level from
ice on 4 Myr samples (mean / worst / share below -150 m / share below -430 m), old = 4ce59df:

| seed | old | new (PW-366) |
|---|---|---|
| 3199 | -26 / -207 / 4% / 0% | -82 / -368 / 19% / 0% |
| 11 | -55 / -563 / 11% / 6% | -92 / -609 / 18% / 7% |
| 2 | -92 / -447 / 21% / 2% | -112 / -542 / 25% / 5% |
| 21 | -19 / -131 / 0% / 0% | -75 / -510 / 17% / 5% |

Run time +10-20% (604-719 s -> 709-878 s per L6 Gyr). The planets recover (no runaway), but 3 of 4 seeds
now pass the ~-430 m bar PW-240 already called too deep. Nothing was clamped.
Options:
- A. Accept: the thicker profile is Earth's (Antarctica's real extent fits ~75 kPa); deep eras are the
  geography's (continents over the poles, PW-364).
- B. PW-240's lean: a stronger thermostat on the climate drift (smaller `climate_drift` sd, ~2 C), so cold
  eras are rarer and shorter; ice volume per era stays physical.
- C. Weaker local damping (`icemass.LOCAL` 0.3 -> 0.15) to trim the snowier margins.
Lean: B (it addresses how often the eras happen, not the ice physics PW-366 just aligned with the time zoom).
- [ ] decide; re-run the 4-seed table after

## Updates
- 2026-10-19: Coordinator decision 2026-10-19 (owner delegates physics): option B, a smaller climate_drift sd (~2 C). Re-run the 4-seed L6 table after.
- 2026-10-19: Created from inbox draft draft-cold-eras-deeper-after-pw366.md (found by pw366).
