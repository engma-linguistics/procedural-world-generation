---
id: PW-876
title: Reef growth tests the annual air temperature against reef_temp, which is documented as sea-surface temperature
type: task
status: done
parent: null
milestone: null
subsystem: surface
effort: xs
impact: low
found_by: coupling-audit
blocked_by: []
relates: []
refs: [planet/tectonics/earth.py, planet/tectonics/volcanism.py, planet/coastal.py, docs/review/coupling-audit/]
created: 2026-10-25
updated: 2026-10-27
---

## Description
Coupling audit finding C7 (severity low for the Earth-like v1 finish; docs/review/coupling-audit/README.md).

**One side:** planet/tectonics/earth.py reefs() (main L787): reef where sim.temp >= p.reef_temp; volcanism.py L393 likewise builds an "sst" from sim.temp.

**Other side:** planet/tectonics/params.py reef_temp "C, annual mean sea surface"; climate.compute returns sst (currents, upwelling, overturning), used by coastal.py for living reefs.

**Why they disagree:** The run's reefs and the world's coastal reefs use different temperatures for the same threshold.

**Measured:** Shallow sea (-1500..-5 m) in worlds 2a7385, e71172, 6909cb, a12762: air is 1.5-2.0 C colder than SST on average; cells passing 23.5 C by air are 4-16% fewer than by SST.

**What to try:** Keep the climate's sst on the sim (sim.sst) and test it, or lower reef_temp by ~1.7 C and relabel it as air.

## Updates
- 2026-10-27: Status todo -> done. Merged v1-finish-17 (paired with main on two rolls: indistinguishable).
- 2026-10-25: Created from inbox draft draft-reefs-read-air-temperature-as-sea-surface.md (found by coupling-audit).
