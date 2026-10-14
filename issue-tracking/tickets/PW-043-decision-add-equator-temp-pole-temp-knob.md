---
id: PW-043
title: "Decision: add equator_temp / pole_temp knobs?"
type: task
status: needs-decision
parent: null
subsystem: climate
effort: xs
impact: low
found_by: overview
blocked_by: []
relates: []
refs: [planet/climate.py, planet/tectonics/params.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
The README used to claim `equator_temp`/`pole_temp` params; they don't exist (README fixed in f45525c).
`climate.compute` derives the equator and pole temperatures from `climate_offset` (dT) and tilt, so a
hothouse or cold world is set by those two.
- **A:** add the two knobs as params (overriding the derived values), e.g. for a flat-gradient hothouse.
- **B:** don't; dT and tilt cover the use cases, and fewer knobs keep runs comparable.

Coordinator's lean: B (close as wontdo) unless you want worlds with an unusual equator-to-pole gradient.

## Updates
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Viewer / Earth world.
