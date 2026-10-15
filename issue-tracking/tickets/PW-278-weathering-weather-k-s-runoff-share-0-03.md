---
id: PW-278
title: "Weathering: WEATHER_K's runoff share (0.03/C) double-counts rain already in the erosion rate"
type: task
status: in-progress
parent: PW-245
subsystem: climate
effort: xs
impact: low
found_by: audit-ice-veg
blocked_by: []
relates: [PW-235, PW-240]
refs: [planet/tectonics/earth.py, docs/review/audit/ice-veg.md]
created: 2026-10-15
updated: 2026-10-15
---

## Description
`earth.WEATHER_K` = 0.12/C is documented as 0.09 (GEOCARB's activation energy) + 0.03 (runoff). The weathering
sink is `sim.removed x exp(WEATHER_K (T - 15))`, and `removed` is erosion, which already scales with rain
((P/800)^0.8, §2.5). The runoff part is therefore counted twice.

It was raised from 0.06 in PW-235 to shorten cold eras (a metric). Set it to 0.09 and re-check PW-240's
cold-era table: expect slightly longer and colder cold eras.

## Updates
- 2026-10-15: Status todo -> in-progress. Fix agent started (owner approved leans, 2026-10-15).
- 2026-10-15: Created from inbox draft draft-audit-ice-veg-weathering-runoff-twice.md (found by audit-ice-veg).
