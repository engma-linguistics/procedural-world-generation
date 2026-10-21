---
id: PW-501
title: Passes through narrow ranges are missed at world scale (Pyrenees, Caucasus)
type: task
status: todo
parent: PW-099
milestone: null
subsystem: surface
effort: s
impact: low
found_by: humanuse
blocked_by: []
relates: [PW-099]
refs: [planet/humanuse.py]
created: 2026-10-21
updated: 2026-10-21
---

## Description
`humanuse.passes` finds the lowest crossing between each pair of touching drainage basins where one basin is >= 300000 km2 and the other >= 25000 km2, with 300 m of relief over the valley floors on both sides. On f6e955 (L6) the Alps (817 and 1382 m), the southern and central Andes (1862, 4107, 4311 m) and the Rockies appear, but the Pyrenees, the Caucasus and the Himalaya passes are missing: those ranges are only one or two cells wide, so cell means give less than 300 m of relief, or the two sides drain to the same outlet. Zoom passes (2 km pixels, 150 m relief) are not affected. A second rule (topographic saddles by sign changes around a cell ring, with a prominence floor) would find divides inside one basin too. Needs a look at whether it is worth it for the world layer or whether the zoom is the right place.
- [ ] decide: accept (world passes are only the big ones) or add the saddle rule

## Updates
- 2026-10-21: Created from inbox draft draft-humanuse-coarse-passes.md (found by humanuse).
