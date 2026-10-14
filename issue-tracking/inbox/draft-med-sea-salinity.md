---
title: "Earth: Mediterranean and Red Sea too fresh and cool (salinity 35.7 / 37.4 psu)"
type: task
status: todo
parent: null
subsystem: ocean
effort: m
impact: low
found_by: viewerocean
blocked_by: []
relates: [PW-016]
refs: [planet/ocean.py, planet/climate.py, "world 64fc00"]
---

## Description
With salinity and SST now stored (PW-137 / PW-144), Earth (world 64fc00) shows the
marginal seas too fresh: Mediterranean 35.7 psu at 35 N 18 E (observed ~38.5), Red Sea
37.4 (observed ~40), Persian Gulf 38.2 (observed ~40); and the Mediterranean too cool
(SST 15.4 C annual, July 18.9; observed ~19-20 annual, ~26 in August). Global pattern is
right (Atlantic saltier than the Pacific, fresh Arctic and Bay of Bengal, salty
subtropics). Likely causes: the coarse (level-5) overturning grid mixes the narrow
seas with the open ocean through their straits, and salinity is carried / relaxed
regardless of the sill. Matters for a Mediterranean outflow analogue and for which
marginal seas could make deep water on other worlds.
