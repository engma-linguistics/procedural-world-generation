---
id: PW-665
title: "Peoples: groups within a people (cultures and ways of life: steppe/forest orcs, human seafarers/farmers/nomads)"
type: story
status: todo
parent: PW-103
milestone: v2
subsystem: timezoom
effort: l
impact: high
found_by: peoples-workbench-lane
blocked_by: []
relates: [PW-650, PW-661]
refs: [docs/proposals/lineages.md, planet/lineages/spec.py, planet/lineages/history.py, viewer/lineages.html]
created: 2026-10-23
updated: 2026-10-23
---

## Description
Owner (2026-10-24): distinct groups within a people. These are cultures and ways of life, not genetic
subspecies. Each group shares its people's ancestry and identity but has its own niche, traits, demography,
land use and wishes, and spreads as a range of its own. The workbench lane had no budget left to build it.

The design is in docs/proposals/lineages.md, "Next: groups within a people":
- origin kind `group` with `group_of`;
- appearance by divergence where the group's niche beats its people's;
- free mixing with its people and its sister groups (no closed-country term);
- a per-people roll-up in the summaries, with the groups' own rows in results and stories;
- the Peoples tab expands a people to its groups.

- [ ] `origin = "group"` parsed, inherited from the people, never ending its parent
- [ ] divergence placement; free mixing with kin groups
- [ ] people roll-ups in `meta.present` and run.txt; the groups' rows and stories
- [ ] workbench: expandable groups in the Peoples tab, grouped rows in Results
- [ ] preset: steppe/forest orcs; human seafarers/farmers/nomads; runs on 1df1c3 and 3e9e7d

## Updates
- 2026-10-23: Created from inbox draft draft-peoples-groups.md (found by peoples-workbench-lane).
