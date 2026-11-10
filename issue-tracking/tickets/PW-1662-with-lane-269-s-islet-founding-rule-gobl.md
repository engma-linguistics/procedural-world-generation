---
id: PW-1662
title: With lane 269's islet founding rule, goblins on af2677 end at about half their range on main (median 4.1 -> 2.4 Mkm2)
type: task
status: todo
parent: null
milestone: later
subsystem: peoples
effort: s
impact: low
found_by: lane269b
blocked_by: []
relates: [PW-1558, PW-1182]
refs: ["planet/lineages/history/origins.py::_founders_room", "planet/lineages/history/origins.py::_origin_split", "planet/lineages/history/dispersal.py::_refuge_cell", tools/peoples_robust.py, docs/review/peoples/origins-spread.md, "branch lane269b (lane 269 PW-1558 suite, af2677 arm now; scratch outputs deleted)", "world af2677"]
created: 2026-11-10
updated: 2026-11-10
---

## In plain words
Lane 269 stops new peoples being born on a tiny islet. On world af2677 that moves the goblinoid stem about 1,600 km to a big
continent. The goblins born from it later now end smaller than on main: about 2.4 million km2 instead of 4.1 (still above the
1 million km2 floor). If nobody checks, goblins quietly become a minor people in every dnd history on this world.

## Description
Suite af2677, arm now, 22 runs; baseline main 673436c0, branch lane269b (c6907d5b + main 31c3b00d): goblin min 2.13 -> 1.91 Mkm2,
median 4.13 -> 2.43; dnd share median 0.28% -> 0.15%. The goblinoid stem is now founded off the mammal islet ("no founders'
country on the parent's islet: the nearest free country", 1,566-1,754 km), and its daughters start on the continent the human line
also starts on (human median 23.7 -> 39.4 Mkm2). Check whether goblins are hemmed in by humans there (as goliaths are, see
PW-1558's update) once PW-1558 settles; it may resolve with PW-1182. If goblins never fall under 1 Mkm2, this can be closed as
an accepted shift.

## Updates
- 2026-11-10: Created from inbox draft draft-goblins-shrink-with-islet-founding-fix.md (found by lane269b).
