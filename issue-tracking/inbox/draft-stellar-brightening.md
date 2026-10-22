---
title: "The star brightens over a run (~0.9% per 100 Myr for a Sun-like star): a slow, planet-relative term in dT; optional variable star"
type: task
status: todo
parent: PW-470
milestone: v2
subsystem: climate
effort: s
impact: med
found_by: ice-v2-stage0
blocked_by: []
relates: [PW-555]
refs: [planet/orbit.py, planet/tectonics/earth.py, docs/review/ice-v2-criteria.md]
---

## Description
Base assumption A9 (docs/review/ice-v2-criteria.md): S0 is fixed at 1361 W/m2 and dT has no solar term. A
Sun-like star brightens ~0.9% per 100 Myr now (Gough 1981), so a 2 Gyr run spans ~17% of luminosity: tens of C of
forcing that the weathering thermostat should mostly absorb (the faint young Sun, Feulner 2012). Add it as a
planet-relative term (the luminosity against the run's start, a `star_age` param, sensitivity from the forcing
~ S/4 (1 - albedo) x the model's ~0.6 C per W/m2), and check on the 10 seeds that the thermostat absorbs it (CO2
falls through the run). Optional generation-time `star_variability` (period, amplitude) as a world-builder input
the recovery/onset lever can use: real luminosity trends are far too slow to switch ice ages on or off on Myr
scales, so a "solar help" lever is a world-builder control unless the star is set up as variable.
- [ ] term in global_temperature, off by default until measured
- [ ] 10-seed 2 Gyr L6 check: CO2 index trends down, icehouse share within N3
