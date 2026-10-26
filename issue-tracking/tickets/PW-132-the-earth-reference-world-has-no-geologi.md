---
id: PW-132
title: The Earth reference world has no geological record, so no landform classes
type: task
status: todo
parent: null
milestone: later
subsystem: surface
effort: m
impact: low
found_by: landform
blocked_by: []
relates: [PW-009, PW-649]
refs: [tools/earth_world.py, planet/landform.py]
created: 2026-10-14
updated: 2026-10-26
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

## Updates
- 2026-10-26: Parent PW-005 (done) -> none. (PW-900 backlog reorg).
- 2026-10-23: Filed under the quality-pass epic PW-649 (relates PW-649, milestone later): shipped and judged good enough, residual kept for a later cleanup pass.
- 2026-10-14: Created from inbox draft draft-earth-world-landforms.md (found by landform).
