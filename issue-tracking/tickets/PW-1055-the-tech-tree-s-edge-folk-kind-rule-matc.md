---
id: PW-1055
title: The tech tree's edge_folk kind rule matches no people; which peoples should start with its kit?
type: task
status: needs-decision
parent: null
milestone: null
subsystem: timezoom
effort: xs
impact: low
found_by: fix-lane-49
blocked_by: []
relates: [PW-1041, PW-946]
refs: [planet/lineages/samples/techtree.toml, planet/lineages/samples/dnd.toml, planet/lineages/samples/seven_meals.toml, planet/lineages/techtree.py]
created: 2026-10-30
updated: 2026-10-30
---

## Description
In plain words. The tech tree has a rule that gives the "edge folk" a starting kit (language, song, foraging lore, shellfish). But no people is called edge_folk. The name belongs to a nickname that others give a people ("folk from beyond the edge", an `[[exonym]]` in both preset trees). So the rule never applies. Since PW-1041 (fix lane 49), the tech tree prints a warning about it every time it is built.

I couldn't tell from the code or the tickets which peoples the rule was meant for, so I left it as it is. Options:
- A. Delete the rule. The peoples it was meant for already start like their parents.
- B. Point it at real line ids (`of` now takes a list), for example the arrivals that come from beyond the world's edge, if those are what was meant.
- C. Make kind rules able to match an exonym, so every people that gets the "edge folk" nickname in a run starts with the kit. This is new behaviour, and it would depend on the run's reputation pass.

Lean: A, unless the owner remembers a specific people for it. Also: Seven Meals has no `triton` and no saurian lines, so those rules warn there too. That's correct, since the tree doesn't have those peoples.

## Updates
- 2026-10-30: Created from inbox draft draft-techtree-edge-folk-kind-rule.md (found by fix-lane-49).
