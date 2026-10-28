---
title: After the PW-936 megafauna fixes, orcs on 1df1c3 and halflings and goblins on 067778 are remnants roll after roll
type: task
status: todo
parent: null
milestone: v2
subsystem: timezoom
effort: m
impact: med
found_by: fun-lane-38
blocked_by: []
relates: [PW-936, PW-924, PW-937]
refs: [planet/lineages/history/megafauna.py, planet/lineages/history/model.py, planet/lineages/spec.py, "worlds 1df1c3 067778 e71172, dnd rolls 7000-7003"]
---

## Description
Fun lane 38 final sweep: 6 planets (2a7385 1df1c3 e71172 6909cb a12762 067778) x dnd rolls 7000-7003, one try each, main against
the final code (PW-936 metapopulation fade, giants at the fliers' reach, PW-937, meta.giant_km2 = 5000, nomads share country, WAY_MOBILE).
The per-people >= 300-cell pass is the same (126/168 = 75% both) and megafauna coverage rises from 48/116 to 106/116 kinds >= 0.5 of
their country on 2a7385 + 1df1c3. Main-people remnants (< 100 cells) go from 18 to 24, but the new ones are not scattered one-offs:
- 1df1c3: orcs at 17 cells on 3 of 4 rolls (main: orcs pass on all 24 runs).
- 067778: halflings 38/46 and goblins 62-88 on rolls 7000-7002 (main: one goblin remnant there).
- e71172/7000: dwarves 4, goblins 44.
The owner accepts an occasional small range, not a pattern; these two are patterns. Likely cause: the megafauna now hold most of
their country there (scatter reaching far, the fade linking pockets) and the peoples still feel them at MEGAFAUNA_PUSH x overlap,
or the hill giants (pastoral nomads, now sharing at NOMAD_COEXIST) took the orcs' hills; not split by a variant.
- [ ] per-line attribution on 1df1c3 (which rival takes the orcs' room) and on 067778 (halflings, goblins)
- [ ] fix at the cause; re-run the 6 x 4 sweep: remnants back to main's level, pass >= 70%, coverage held

## Updates
- 2026-10-28: Created.
