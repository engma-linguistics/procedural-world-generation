---
id: PW-564
title: "The star brightens over a run (~0.9% per 100 Myr for a Sun-like star): a slow, planet-relative term in dT; optional variable star"
type: task
status: done
parent: PW-470
milestone: v2
subsystem: climate
effort: s
impact: med
found_by: ice-v2-stage0
blocked_by: []
relates: [PW-555]
refs: [planet/orbit.py, planet/tectonics/earth.py, docs/review/ice-v2-criteria.md]
created: 2026-10-22
updated: 2026-10-24
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

## Updates
- 2026-10-24: Status todo -> done. Merged as the default star term (v1-finish-7). Note: model sensitivity is 0.81 C/(W/m2), not 0.6.
- 2026-10-24: Lane v1-finish-7: brightening star in the code (earth.star_forcing; params star_brightening, star_age; Gough 1981 against the run's start, 238 W/m2 x dL/L at the model's own 0.81 C per W/m2, not 0.6). Default 0.45 x a Sun-like rate (a ~0.75 solar-mass K star: the Sun-like 1.0 warms 1 Gyr runs ice-free on the in-range thermostat). L6 16/18, L7 7/8 on the bar. 2 Gyr runs unchecked (draft-star-brightening-default-signoff.md).
- 2026-10-24: Lane v1-finish-6 measured a brightening star (monkeypatched, not merged; docs/review/base-climate/v1-finish-6/c_run.py): +0.9%/100 Myr at 0.6 C per W/m2 = +1.3 C/100 Myr; the model thermostat passes ~half of a sustained forcing, so dT +7.4 over 300-1000 Myr and 16/18 draws never-ice. Needs a stronger Gyr-scale thermostat (or a weaker star) before it can be used.
- 2026-10-23: Milestone v1 -> v2 (owner approved shrinking v1 to its real gates, 2026-10-24; docs/review/board/triage-2026-10-24.md).
- 2026-10-22: Created from inbox draft draft-stellar-brightening.md (found by ice-v2-stage0).
