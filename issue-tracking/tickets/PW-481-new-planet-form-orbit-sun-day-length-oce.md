---
id: PW-481
title: "New planet form: orbit, sun, day length, ocean fraction, atmosphere and planet size are not parameters yet"
type: story
status: todo
parent: PW-244
milestone: v2
subsystem: climate
effort: l
impact: med
found_by: agent-make-ui
blocked_by: []
relates: [PW-472, PW-248, PW-443]
refs: [planet/make.py, planet/tectonics/params.py, planet/orbit.py, viewer/start.js]
created: 2026-10-20
updated: 2026-10-23
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

## Updates
- 2026-10-23: Merged PW-219 (closed as duplicate; PW-597 triage): this ticket's scope already lists planet size and gravity as the last parameter in its suggested order. PW-219's content for that step: radius, mean density and makeup other than Earth's change gravity (mountain heights, isostasy, erosion), internal heat and so plate speed and volcanism, the grid's km per cell, atmosphere and ocean scaling, and climate (Coriolis with day length). It needs a review of every Earth constant hard-coded across planet/ before anything else; more guesswork-heavy than the moons; effort for that step alone was xl.
- 2026-10-20: Created from inbox draft draft-make-settings-gaps.md (found by agent-make-ui).
