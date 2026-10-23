---
id: PW-665
title: "Peoples: groups within a people (cultures and ways of life: steppe/forest orcs, human seafarers/farmers/nomads)"
type: story
status: done
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
updated: 2026-10-24
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

- [x] `origin = "group"` parsed, inherited from the people, never ending its parent
- [x] divergence placement; free mixing with kin groups
- [x] people roll-ups in `meta.present` and run.txt; the groups' rows and stories
- [x] workbench: expandable groups in the Peoples tab, grouped rows in Results
- [x] preset: steppe/forest orcs; human seafarers/farmers/nomads; runs on 1df1c3 and 3e9e7d

## Updates
- 2026-10-23: Scope (owner 2026-10-24): a group is only a way of life within a people (habitat niche, traits, land use, wishes); languages, religions, customs, cultural spread or assimilation and cultural effects on peoples belong to PW-661.
- 2026-10-23: Created from inbox draft draft-peoples-groups.md (found by peoples-workbench-lane).
- 2026-10-24: Built by peoples-groups-lane (docs/proposals/lineages.md, "Groups within a people"). Groups take up every cell of their people's range where their habitat beats the people's by GROUP_MARGIN 0.15; they mix as kin (GROUP_KIN 0.5, no exclusion); hybrids, hosts and wishes see a people as a whole; meta.present.peoples roll-ups, the peoples_whole layer, workbench groups (Peoples, side panel, Results) and the globe toggle. Preset: steppe/forest orcs; human farmers, herders, nomads, seafarers; hill dwarves. Runs 8bac4d (1df1c3) and c646ea (3e9e7d) replace 37e9da and 33b1c3: seafarers hold coasts (100% coast), nomads desert/steppe, herders open land, hill dwarves hills, forest orcs forest; steppe orcs hold the steppe on 3e9e7d but stay thin on 1df1c3, where the orcs already are steppe folk. Shares: draft-peoples-group-shares.
