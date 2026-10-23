---
id: PW-152
title: "Earth: Mediterranean and Red Sea too fresh and cool (salinity 35.7 / 37.4 psu)"
type: task
status: todo
parent: PW-649
milestone: later
subsystem: ocean
effort: m
impact: low
found_by: viewerocean
blocked_by: []
relates: [PW-016]
refs: [planet/ocean.py, planet/climate.py]
created: 2026-10-14
updated: 2026-10-23
---

## Description
With salinity and SST now stored (PW-137 / PW-144), Earth (world dc3732 (deleted)) shows the
marginal seas too fresh: Mediterranean 35.7 psu at 35 N 18 E (observed ~38.5), Red Sea
37.4 (observed ~40), Persian Gulf 38.2 (observed ~40); and the Mediterranean too cool
(SST 15.4 C annual, July 18.9; observed ~19-20 annual, ~26 in August). Global pattern is
right (Atlantic saltier than the Pacific, fresh Arctic and Bay of Bengal, salty
subtropics). Likely causes: the coarse (level-5) overturning grid mixes the narrow
seas with the open ocean through their straits, and salinity is carried / relaxed
regardless of the sill. Matters for a Mediterranean outflow analogue and for which
marginal seas could make deep water on other worlds.

## Updates
- 2026-10-23: Filed under the quality-pass epic PW-649 (parent PW-649, milestone later): shipped and judged good enough, residual kept for a later cleanup pass.
- 2026-10-23: PW-597 triage (2026-10-23): kept, not wontdo. It points at a mechanism (the coarse overturning grid mixes narrow seas with the open ocean through their straits; salinity is relaxed regardless of the sill), not only an Earth miss. Mirror of PW-324.
- 2026-10-14: Created from inbox draft draft-med-sea-salinity.md (found by viewerocean).
