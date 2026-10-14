---
id: PW-066
title: "Zoom: lake-outlet cone can raise low ground up to 150 km away"
type: task
status: done
parent: null
subsystem: zoom
effort: s
impact: low
found_by: falls
blocked_by: []
relates: []
refs: [planet/zoom.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
The cone that steps the ground down below an open lake's outlet (at most 2 m/km, rapids) can raise low
ground up to 150 km around the outlet. Limit it to the outlet river's corridor.

## Updates
- 2026-10-14: Status todo -> done. zoomsmalls: rapids floor only on the outflow and its banks (banks(), 4 km then 30 m/km), capped at the coarse ground, restored after creep. 7 lake zooms: px raised > 1 m by the last lake's ramp 30,426 -> 3,533. Leftover (high mountain lakes) in an inbox draft.
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Highlights (falls).
