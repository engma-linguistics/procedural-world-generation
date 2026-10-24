---
id: PW-697
title: Arrivals from outside the world (elves, gnomes, tritons) land on one landmass only
type: task
status: done
parent: PW-103
milestone: v2
subsystem: timezoom
effort: s
impact: low
found_by: fill2
blocked_by: []
relates: [PW-683]
refs: [planet/lineages/history.py, planet/lineages/samples/dnd.toml]
created: 2026-10-23
updated: 2026-10-23
---

## Description
An 'arrival' people is placed at one best-habitat site, so it begins on one landmass and must cross seas like anyone else (elves have sea share 0.3, gnomes 0.1). Options: (A) leave it (one portal; the sea crossings decide), (B) found it on the best site of each of the N largest landmasses ("the Feywild opens in several places"), (C) a `places` list per arrival in the preset. PW-683 asked for this. After the pioneer fix (fill2) far continents fill from any landing, so (A) is no longer what leaves land empty; my lean is A.

## Updates
- 2026-10-23: Status todo -> done. Merged (fun lane 4, bfddaaf): see docs/proposals/lineages.md 'Fun lane 4'.
- 2026-10-23: fun4: built. meta.portal_mode off|random|sites, portals N, portal_sites; workbench + CLI --portal-mode/--portals. 3 portals move the mean wish +0.01..+0.03 on 1df1c3/3e9e7d (4 tries each); default stays off. Site approximations: draft-portal-sites-extinct-volcanoes-and-reefs.
- 2026-10-23: Status needs-decision -> todo. Owner (2026-10-24): a toggle: one portal, or N portals, placed at random or tied to interesting sites (the deepest part of a large forest, the middle of a desert, a coral reef, the foot of an extinct volcano...).
- 2026-10-23: Created from inbox draft draft-arrivals-from-outside-pick-several-landmasses.md (found by fill2).
