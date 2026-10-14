---
title: The Earth reference world has no geological record, so no landform classes
type: task
status: todo
parent: PW-005
subsystem: surface
effort: m
impact: low
found_by: landform
blocked_by: []
relates: [PW-009]
refs: [tools/earth_world.py, planet/landform.py]
---

## Description
PW-009 asked to check the class map on the Earth world where possible. Earth
worlds (`tools/earth_world.py`) are built from observed terrain, with no
simulated history (no strata, rift or fold dates), so `landform.classify`
has nothing to read and the world has no `landform` layer. To compare the
classes against Earth one would need the record from observed geology, e.g.
GLiM lithology for the top stratum, a tectonic-age map (rift and orogeny
ages) and known LIPs, mapped onto `tectonics.record` columns. Only worth it
if an Earth comparison of the class shares becomes a calibration target.
