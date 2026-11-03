---
id: PW-1382
title: "Den-dwelling peoples follow the rock: caves, rock shelters and burrowable ground from the geology"
type: task
status: done
parent: null
milestone: v2
subsystem: peoples
effort: m
impact: med
found_by: Daniel 11-02
blocked_by: []
relates: [PW-1275, PW-007, PW-012]
refs: ["planet/lineages/ladder.py::is_den"]
created: 2026-11-02
updated: 2026-11-03
---

## Description
In plain words: Daniel asked whether the real world has enough caves for den-dwelling peoples (goblins, kobolds and the like), and agreed that dens should follow the geology. Today a den kind (ladder.py: is_den) gets its den living anywhere. Proposal: the land's chance of holding dens comes from the bedrock and the landforms (karst limestone, lava fields, cliffs and gorges with rock shelters, soft ground to dig), so den peoples cluster where the rock allows and are thin elsewhere. Scope first: which rock and landform fields the world already has (PW-007, PW-012), then a den-fitness field per cell feeding the ladder's den factor. Measure the den kinds' range and share on the robust suite.

## Updates
- 2026-11-03: Status in-progress -> done. Lane 143 merged (2ba59119): dens.fitness from rock/landform/loess (karst 1.0 ... crystalline relief 0.4); den kinds at half density on no den ground, full on the best; habitat never reads it. 14 D&D runs vs main: kobold range 11.1 -> 10.2 Mkm2 (on den ground 35 -> 41%), goblins 4.2 -> 5.1 Mkm2 (9 -> 15%); old broken-country rule removed. Full suite 957 passed. Write-up docs/review/peoples/dens/round1.md.
- 2026-11-03: Status todo -> in-progress. Lane 143 started 11-03.
- 2026-11-02: Daniel 11-02: let the den-inclined kinds prefer good den ground, never rely on it. Goblins, kobolds and the like live all over; den fitness is a preference (a density/settling bonus), not a requirement or a range limit.
- 2026-11-02: Created.
