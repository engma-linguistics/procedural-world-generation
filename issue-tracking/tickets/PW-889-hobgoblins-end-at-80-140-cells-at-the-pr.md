---
id: PW-889
title: Hobgoblins end at 80-140 cells at the present on the small-continent tries once the humans invade the front (PW-887)
type: task
status: done
parent: PW-692
milestone: v2
subsystem: timezoom
effort: s
impact: low
found_by: fun-lane-29
blocked_by: []
relates: [PW-887]
refs: [planet/lineages/history.py]
created: 2026-10-25
updated: 2026-10-30
---

## Description
With the frontier-invasion term (history.INVADE 0.5, floor 0.3) the humans on the small continent of 2a7385 (tries 7000, 7005, 7006) take the thinner peoples' cells along the front. The hobgoblins, 2.4-2.6k cells at 20 kyr ago, end at 82-141 cells at the present (209-484 before; they were already thin in the Holocene farmers' squeeze); the lizardfolk on 7005 292 -> 206; orcs unchanged within noise. Decide whether ~100 cells is viable for a fantasy people (a refuge floor) or whether INVADE should be lower than 0.5 / the floor higher. Also, the crowding drive (CROWD_HOP 2, CROWD_ENTER 0.5) moved the ranges under 5% in these tries; it matters mostly when a craft rung opens a crossing, so a later check on boat-era crossings is open. Elves on 7003 fell 2765 -> 814 (still >= 500).
- [ ] decide on a hobgoblin refuge floor or a lower INVADE; re-measure over 8 seeds

## Updates
- 2026-10-30: Status needs-decision -> done. Fun lane 54: done, as two mechanisms. (1) Cohabitation: a new pair wish 'among' (a people lives readily inside a friendly people's country: competition between them cut by AMONG_TOLERANCE 0.7 x weight, and no frontier invasion), and pressure-driven integration (a squeezed people feels up to INTEGRATE 0.5 less competition from each neighbour, scaled by its squeeze and the cohabitation matrix). dnd: bugbears among goblins and hobgoblins, goblins among hobgoblins 0.8, halflings among humans 0.8, gnomes among dwarves 0.6. (2) City minorities: a group with cities = true lives as a share of the townsfolk in its hosts' densest settled cells (top 5% of the peopled land, at least 5/km2) within 1000 km of its own country, counted in its people's numbers, not its range; dnd city goblins 3%, city kobolds 2%, since 5 kyr. Both editable in the lineages editor (Wishes: 'among'; Peoples: 'lives in other peoples' cities', 'share of the townsfolk'). Paired run against b8dcfb2d, world af2677 (L6), 8 rolls: per-people pass (300+ cells) 93/184 = 50.5% -> 97/184 = 52.7%; bugbears median 152 -> 497 cells (pass 2 -> 6), halflings 768 -> 1209, orcs 971 -> 1037, goliaths 86 -> 96, elves 536 -> 450 (pass 6 -> 5). City kobolds in 8 of 8 rolls (77-238 cells, 0.41-0.80 M people), city goblins in 4 of 8 (the goblins' country is over 1000 km from any big town in the others). World 2a7385 (L7), 2 rolls: pass 31/46 both; the refuges of roll 7000 stay refuges (orcs 5 -> 9, halflings 7 -> 4: cut off across the sea from the humans; goliaths 111 -> 154). Troglodytes 0 in every run: the preset makes them extinct at 60 kyr (in one roll they died out at 900 kyr with 4,000 cells of good habitat: competition, not habitat). Hobgoblins on af2677 stay at ~10 cells in both arms (an island start; draft).
- 2026-10-29: Owner 10-29: also 'stuff can be two things'. One species can live as a persecuted, untrusted minority inside big cities (goblins, kobolds, as in the Forgotten Realms) and in caves in the countryside at once. Build on the existing groups-within-a-people (PW-665): an urban-minority group of a people living in another people's settlements, beside its own wild country. Relates PW-928's pressure-driven moves and PW-856's predominant species per settlement.
- 2026-10-29: Owner 10-29: an occasional refuge group (~100 cells) is fine; worlds needn't end balanced. Idea: cohabitation preferences between peoples (bugbears happy among goblins and hobgoblins, and others similarly), so a squeezed people can share a friendly people's land instead of losing it. A stronger form: under pressure a people grows more willing to integrate with a neighbour, as a survival strategy. Coordinator to design.
- 2026-10-25: (fun-lane-30) With PW-888 origins, hobgoblins at the present on tries 7000/7005/7006 of 2a7385: 7406/12479/6317 cells (82/92/141 before); the other five tries 3.1-8.5k. Different draws of origin, so not the same worlds of peoples as before.
- 2026-10-26: Milestone null -> v2. (PW-900 backlog reorg).
- 2026-10-25: Created from inbox draft draft-hobgoblins-thin-out-under-frontier-invasion.md (found by fun-lane-29).
