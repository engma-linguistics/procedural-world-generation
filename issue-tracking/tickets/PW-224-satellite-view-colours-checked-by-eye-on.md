---
id: PW-224
title: Satellite view colours checked by eye only; calibrate against real imagery
type: task
status: todo
parent: null
subsystem: viewer
effort: m
impact: low
found_by: satview
blocked_by: []
relates: [PW-083]
refs: [planet/satellite.py, "world fe2af4", docs/overview/satellite_view.jpg]
created: 2026-10-15
updated: 2026-10-15
---

## Description
The satellite view (PW-083, `planet/satellite.py`) uses hand-picked sRGB colours per plant type
(leaf-on / leaf-off), soil, rock, snow, ice and water, tuned by eye against Blue Marble-style imagery on
the Earth world fe2af4. It looks plausible (Sahara tan, Sahel green in July, red-tan Australia, white
winter Siberia with grey forest), but nothing measures it. A check could compare the Earth world's
`sat_jul` with a downsampled Blue Marble (NASA, public domain) cell by cell on land where the model's
vegetation agrees with potential vegetation (so climate errors don't count), and fit the palette's
leaf-on colours, soil colours and the snow cover scale (SNOW_SWE) to it.
- [ ] a `tools/` check printing mean colour error by biome group, and a refit of the palette

## Updates
- 2026-10-15: Created from inbox draft draft-satellite-palette-check.md (found by satview).
