---
id: PW-933
title: "PW-874 remainder: climate.compute / months / icemass still see today's S0, not the run's star"
type: task
status: todo
parent: null
milestone: v1
subsystem: climate
effort: s
impact: low
found_by: v1-finish-17
blocked_by: []
relates: [PW-874]
refs: [planet/climate.py, planet/orbit.py, planet/tectonics/earth.py]
created: 2026-10-27
updated: 2026-10-27
---

## Description
Lane v1-finish-17 did not land PW-874's fix: PAR, Oudin PET, the sea's seasonal swing, icemass and the orbital
anomalies all still use S0 = 1361 W/m2 (planet/orbit.py, climate.S0_MJ), while the run's star is L/L_now 0.92 at the
start of a 1 Gyr run (0.85 at 2 Gyr, +-4% under the star thermostat). Exact at the run's end, so default worlds
are fine; earlier moments and thermostatted runs get PAR/PET ~8-15% too high.
- [ ] pass the star's L/L_now (from the run's frame stats) into climate.compute, months and icemass as one scale on S0
- [ ] re-measure with fmtally (L6 18 draws, L7 8 draws, two re-rolled offsets: one 18-draw roll swings by ~6 passes, see draft-l6-passrate-roll-noise)

## Updates
- 2026-10-27: Created from inbox draft draft-pw874-remainder-star-scale-on-s0.md (found by v1-finish-17).
