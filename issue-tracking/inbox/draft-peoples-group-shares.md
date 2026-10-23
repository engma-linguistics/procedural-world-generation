---
title: "Peoples groups: how much of a people takes up a way of life (seafarers ~1% of humans; steppe orcs thin where the orcs already are steppe folk)"
type: task
status: needs-decision
parent: PW-649
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: peoples-groups-lane
blocked_by: []
relates: [PW-665]
refs: [planet/lineages/history.py, planet/lineages/samples/dnd.toml, docs/proposals/lineages.md]
---

## Description
Groups (PW-665) land where their ways of life fit: human seafarers on coasts (98-100% of their land is coast),
nomads on steppe and desert, herders on open country, farmers on farmland, hill dwarves on hills, forest
orcs in forest. But how big each group gets is set by three knobs nobody has judged yet:
- `GROUP_MARGIN` (0.15): a group takes up land where its own habitat beats its people's by this share;
- the hand-over: half the people's presence in those cells goes to the group at its time;
- `GROUP_KIN` (0.5): a group and its people compete at half their niche overlap, with no exclusion.

At these values (runs on 1df1c3 and 3e9e7d, see PW-665's update) the human row keeps 54-77% of the
humans ("the old ways"), farmers take 19-38%, and seafarers only ~1% (0.9-1.6 Mkm², about half of the
human coast, at a lower density). Where a people already lives the group's way of life (the orcs are a
steppe people in the preset), the steppe group barely differs and stays thin.

Options:
- A: leave as is: the people row is the mainstream, groups are minorities in their niche.
- B: a group takes most of its niche: hand over 0.8 instead of 0.5 and GROUP_KIN 0.35, so seafarers hold
  their coasts outright and the people row thins to the land no group suits better.
- C: preset only: narrow the people rows where a group covers their main way of life (orcs: hills and open
  woodland; steppe orcs: the steppe), keeping the knobs.

Lean: C for the orcs plus A elsewhere; B if the owner wants "the humans" to read mostly as their groups.
