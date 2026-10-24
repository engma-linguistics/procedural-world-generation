---
id: PW-720
title: The peoples' own sea crossings do not yet follow the craft ladder that now gates animals
type: task
status: done
parent: PW-688
milestone: v2
subsystem: timezoom
effort: s
impact: low
found_by: fun6
blocked_by: []
relates: [PW-688, PW-702, PW-675]
refs: [planet/lineages/crossing.py, planet/lineages/animal_defs.py, planet/lineages/spec.py]
created: 2026-10-23
updated: 2026-10-24
---

## Description
`animal_defs.craft_ladder()` (canoe or outrigger 60 kyr, 300 km, dogs and fowl; planked boat 6 kyr, 800 km, sheep and goats;
sailing ship 3 kyr, 2500 km, horses and cattle) decides which animals cross which gaps, with the sea share a people needs to
man each craft (0.05, 0.2, 0.3). People themselves still cross by `crossing.modes` (raft; canoes since CANOES_KYR over
BOATS[1] = 300 km; voyaging since BOATS[3] = 6 kyr to 1500 km), unchanged on purpose so the peoples' draws stay comparable. So
a people can settle an island that its animals only reach later, and the two ladders can drift apart. Make `crossing.modes`
read the same ladder (reach and date per craft) and decide whether the sailing ship should lift the people's reach too.
Also: animals land only on peopled cells (an empty island gets them with its settlers), and a landing is a chance per
0.5 kyr (`BOAT_RATE`), fine for a first pass.
- [ ] one ladder for people and animals

## Updates
- 2026-10-24: Status todo -> done. Merged (fun7, 60c433c); runs b18a68 f78aa8 (fantasy), 3b20dc eda3d7 (real).
- 2026-10-24: Built on branch fun7: crossing.modes reads animal_defs.craft_ladder (canoe 300 km from 60 kyr at sea share 0.02, planked boat 1500 km from 6 kyr at 0.2, sailing ship 2500 km from 3 kyr at 0.3); the ladder's planked reach went 800 -> 1500 km because 800 raised the empty land by 9 points (1df1c3 real, seed 7: 15.9% -> 24.8%).
- 2026-10-23: Created from inbox draft draft-boats-for-peoples-follow-the-craft-ladder.md (found by fun6).
