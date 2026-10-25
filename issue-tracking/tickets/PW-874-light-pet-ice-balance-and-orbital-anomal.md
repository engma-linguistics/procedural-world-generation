---
id: PW-874
title: Light, PET, ice balance and orbital anomalies use today's S0 while the run's star is fainter (or thermostatted)
type: task
status: todo
parent: null
milestone: null
subsystem: climate
effort: s
impact: low
found_by: coupling-audit
blocked_by: []
relates: [PW-809, PW-791]
refs: [planet/orbit.py, planet/climate.py, planet/tectonics/earth.py, docs/review/coupling-audit/]
created: 2026-10-25
updated: 2026-10-25
---

## Description
Coupling audit finding C9 (severity low for the Earth-like v1 finish; docs/review/coupling-audit/README.md).

**One side:** planet/orbit.py S0 = 1361; planet/climate.py S0_MJ (insolation -> PAR, Oudin PET, the sea's seasonal swing, icemass, orbit anomalies, timezoom/plants.py sun).

**Other side:** planet/tectonics/earth.py star_forcing / star_control (branch): L/L_now 0.92 at the start of a 1 Gyr run, 0.85 at 2 Gyr, +-4% under the star thermostat; it enters only through dT.

**Why they disagree:** Same family as the star-frame fix: the star's luminosity is a run quantity, but the radiation the plants, PET and ice see is today's Sun. On the branch it is exact at the run's end, so default worlds are fine; worlds taken earlier, and thermostatted runs, are not.

**Measured:** Arithmetic only: PAR and Oudin PET (both linear in top-of-atmosphere radiation) are 8% too high at the start of a 1 Gyr run, 15% for 2 Gyr; orbital W/m2 anomalies likewise.

**What to try:** Pass the star's L/L_now into climate.compute / months / icemass (one scale on S0), from the run's frame stats.

## Updates
- 2026-10-25: Created from inbox draft draft-insolation-uses-todays-sun-not-the-runs-star.md (found by coupling-audit).
