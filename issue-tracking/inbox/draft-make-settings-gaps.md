---
title: New planet form: orbit, sun, day length, ocean fraction, atmosphere and planet size are not parameters yet
type: story
status: todo
parent: PW-244
subsystem: climate
effort: l
impact: med
found_by: agent-make-ui
blocked_by: []
relates: [PW-472, PW-248, PW-443]
refs: [planet/make.py, planet/tectonics/params.py, planet/orbit.py, viewer/start.js]
---

## Description
PW-472 asked for planet settings "such as orbit, sun or land fraction", but only what the code honours is exposed. Today the New planet form (and `planet make --set`) offers these `tectonics.Params` fields (`make.SETTINGS`): `n_plates`, `start` (supercontinent / scattered), `continental_fraction` (the land-ish knob; there is no ocean fraction or water inventory, `generators.py` says "ocean is whatever's left"), `continental_start`, `heat_start`, `tilt` and `climate_offset`. Presets are the showcase recipes of docs/coordination.md (earthlike, water-world, land-heavy, cold, hothouse).

Not configurable at all (listed in the form under "Not configurable yet", `make.UNSUPPORTED`):
- orbit: distance from the star, eccentricity (only the time zoom's Milankovitch terms in `orbit.py` have any; a run has a fixed orbit);
- star brightness (the climate offset stands in for it: a cold or hot world is a shift of the whole history, not a different insolation);
- day length / rotation rate (the circulation, tides and Coriolis assume Earth's);
- ocean fraction / total water (sea level follows the crust and the ice, not a water volume);
- atmosphere (pressure, CO2 baseline: only the volcanic CO2 index moves);
- planet size and gravity (the grid is Earth-sized, R = 6371 km).

Each is a real piece of model work, and several interact with PW-443 (planet-relative thresholds: weird worlds post-v1). Suggested order if wanted: star brightness + orbit radius as one "insolation" parameter, water inventory, day length, then size.
- [ ] each new parameter added to `tectonics.Params` (or a planet-level params object) and to `make.SETTINGS`, with range and help text
- [ ] `UNSUPPORTED` shrinks accordingly
