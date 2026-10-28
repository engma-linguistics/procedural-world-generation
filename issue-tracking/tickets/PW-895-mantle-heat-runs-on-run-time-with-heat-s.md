---
id: PW-895
title: "Mantle heat runs on run time with heat_start 1: a 2 Gyr run's 2.0 Ga mantle is today's, and its outgassing drifts to ~0.7-0.8 of the spin-up's"
type: task
status: todo
parent: PW-470
milestone: v2
subsystem: tectonics
effort: m
impact: med
found_by: v1-finish-14
blocked_by: []
relates: [PW-859]
refs: [planet/tectonics/earth.py, planet/tectonics/params.py]
created: 2026-10-26
updated: 2026-10-28
---

## Description
`earth.heat(p, t)` decays on run time from heat_start, which is 1.0 by default. The star, by contrast, is dated by
age (now_myr). So a 2 Gyr run has today's mantle at 2.0 Ga, while radiogenic heat was ~1.3-1.5x today's then
(Korenaga 2008). In the ghg set, the source's median over 750-2000 Myr is 0.63-0.97 of the spin-up's reference. At
the bare-ground slope that is about -1 to -3 C.

Dating the heat by the star's age would put more outgassing early, where the faint star needs it. But Korenaga
argues a hotter mantle had slower plates, so the sign on the CO2 flux is debated. This needs a decision, plus a
look at the sea-level and continent paths, which also read heat().

## Updates
- 2026-10-28: Owner 10-28: decide this by going live on the 2 Gyr runs ticket (PW-894), v2 under the ice-age epic.
- 2026-10-26: Held on hold/v1-finish-15-heat: no 2 Gyr gain, L6 1 Gyr all checks 12->9/18, L7 4->2/8. Revisit with 2 Gyr post-v1.
- 2026-10-26: Created from inbox draft draft-mantle-heat-by-age.md (found by v1-finish-14).
