---
id: PW-328
title: "Scattered start: the ocean ages ~0.4-0.9 Myr per Myr in the first 100 Myr, sea falls 150-300 m"
type: task
status: todo
parent: null
subsystem: tectonics
effort: s
impact: low
found_by: pw293
blocked_by: []
relates: [PW-293, PW-051, PW-191]
refs: [planet/tectonics/setup.py, planet/tectonics/events.py, docs/review/audit/pw293-sea-level.md]
created: 2026-10-15
updated: 2026-10-15
---

## Description
With `start=scattered` (not in the health sweep or the showcase recipes) the starting ocean hardly renews in the
first 100 Myr: L5 seeds 1-4, mean ocean age 48 -> 58 / 83 / 93 / 60 Myr at 100 Myr, the basin term's sea
level averaging -54 to -182 m over 0-100 Myr (min -307 m). It isn't PW-293's: with the old 60 Myr start,
seeds 2 and 3 went 60 -> 77 / 108 Myr (-91 / -122 m mean). The supercontinent start renews its ocean at once
(48 -> 31-36 Myr by 100 Myr, the breakup's young floor). Probably the scattered start's continents sit on
every plate, so plates collide instead of spreading until sutures and rifts reorganise them; few ridges, little
new floor. Check whether it settles by ~150 Myr (owner's standard: a convenient start that settles into
realistic behaviour by 50-100 Myr) on a few L6 seeds at 500 Myr; if not, look at where setup's scattered
continents sit relative to plate boundaries.

## Updates
- 2026-10-15: Created from inbox draft draft-scattered-start-ocean-ages.md (found by pw293).
