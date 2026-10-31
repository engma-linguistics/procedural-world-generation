---
title: "Peoples after lane 98's inland pits: humans brittle in dnd again (31x), Seven Meals humans 35% -> 43% on 4360a3"
type: task
status: todo
parent: PW-917
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: lane97
blocked_by: []
relates: [PW-1229]
refs: [docs/review/peoples-brakes/report.md]
---

## Description
**In plain words.** Lane 98 turned the below-sea pits cut off from the ocean into land. The stress suite on lane 97's code with that
change (report, "After merging main") reshuffles the peoples. The humans' share in the full dnd tree on world af2677 swings 20-42%
over the seeds, so they are flagged as brittle again (31x, gone after D27). In Seven Meals on 4360a3 the humans went from 35% to 43%.
The Seven Meals half-orcs died out in one try (j1@af2677), as they did in one try on main.

One suite cannot tell whether this is a real effect of the new land or the usual chaos of a re-rolled draw. The way to tell: compare
the human share over the two worlds and several seeds, before and after, with the land diff per world (inland-pit cells that are now
land, and which peoples hold them).
- [ ] compare over several re-rolled draws (seeds 7, 10, 13 plus jitter) before calling it signal
