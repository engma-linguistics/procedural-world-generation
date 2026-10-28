---
title: Continental hotspot cones top out at ~3 km relief (vent hmax), below the new 4.8 km RELIEF_MAX
type: task
status: todo
parent: null
subsystem: tectonics
effort: s
impact: low
found_by: lane19b
blocked_by: []
relates: [PW-826]
refs: [planet/tectonics/volcanism.py]
---

## Description
PW-826 replaced the 3.5 km absolute continental summit cap with a relief cap above the cone's own ground
(volcanism.top_limit, RELIEF_MAX 4.8 km, Kilimanjaro). Over seeds 1-6 at L6 to 1 Gyr, active continental vents'
relief (top - floor) has median 2577 m, p90 2891, p99 2948, max 3166 m: they hit the per-vent height limit
v["hmax"] set in new_vent long before RELIEF_MAX, so the new cap never binds. (Absolute tops now reach 10.2 km on
high plateaus; that is plateau floor + ~3 km, plausible.) Look at how new_vent draws hmax for continental vents
(now `3000 * U(0.7, 1.1)` m on continents; derive it from the plume supply and lithosphere instead) so the tallest cones reach 4-5 km occasionally.
- [ ] p99 continental cone relief 3.5-4.8 km over seeds 1-6
