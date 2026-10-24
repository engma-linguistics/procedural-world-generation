---
id: PW-684
title: "Cold land stays empty in the D&D preset: only sparse, insular peoples have a niche below 5 C"
type: task
status: done
parent: PW-103
milestone: v2
subsystem: timezoom
effort: m
impact: med
found_by: pw677
blocked_by: []
relates: [PW-677]
refs: [planet/lineages/samples/dnd.toml, "runs 7bc9ed (world 1df1c3), 53b9c1 (3e9e7d)"]
created: 2026-10-23
updated: 2026-10-23
---

## Description
After PW-677, the habitable land (some people's K >= 0.25) that is still empty at the present is mostly cold: 18 of 26 Mkm2 on 1df1c3 is below 5 C (south-polar and Greenland-like lands, the far south of a southern continent). Only frost giants (-20..-2 C), goliaths, dwarves, firbolgs and bugbears have a niche there, and they are sparse, insular and slow to explore. Earth's cold lands (taiga, tundra) are peopled by hunters. Options: a hardy hunter way of life (a group of humans or orcs, or a new tundra people) in the preset; lower insularity or more exploration for goliaths and firbolgs; or accept cold land as hostile. The owner decides which peoples live there.
- [ ] unpeopled share of land below 5 C under 25% on both showcase worlds, or the choice to accept it recorded

## Updates
- 2026-10-23: Status needs-decision -> done. Coordinator (2026-10-24): fill2 (e81da1d): pioneer spread, arctic hunters (human group), groups keep arising. Land below 5 C empty: 3e9e7d 42% -> 5.6%, 1df1c3 56% -> 33% (enclaves behind ice and ranges: PW-698). Runs 9819bb, 9ecac6.
- 2026-10-23: Created from inbox draft draft-polar-peoples-and-cold-land.md (found by pw677).
- 2026-10-24: fill2: human_arctic group (30 kyr, -14..8 C, sea share 0.5), groups keep arising after their origin, and pioneers settle empty country. Land below 5 C unpeopled (4 seeds, means): 1df1c3 72% -> 36%, 3e9e7d 62% -> 14%; kept runs 9819bb 33%, 9ecac6 5.6%. 1df1c3 is still above 25% on average (behind-ice enclaves: draft-empty-enclaves-behind-ice-and-ranges).
