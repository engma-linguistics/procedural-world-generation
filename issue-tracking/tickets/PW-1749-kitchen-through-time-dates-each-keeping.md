---
id: PW-1749
title: Kitchen through time dates each keeping method by the whole people's first knowing it, not the culture's
type: task
status: todo
parent: null
milestone: null
subsystem: food
effort: m
impact: med
found_by: lane309
blocked_by: []
relates: []
refs: ["planet/lineages/kitchen_time.py::events", "planet/lineages/cuisine.py::_known", planet/lineages/techtree.py, planet/lineages/history/tech_live.py, planet/lineages/techspread.py, "runs a2b637, de1cc6 (copies in a scratch dir, since deleted)"]
created: 2026-11-11
updated: 2026-11-11
---

## Description
In plain words: meta.techtree.known holds one date per people and tech (tech -> [kyr ago, how, from]). The culture's kitchen timeline
(kitchen_time.py) and every cuisine sheet's "knows" set (cuisine._known) read that date for every culture of the people. A people that
learnt salting from dwarves on one continent 2,500 years ago shows "salting known (taken up from dwarves)" at that date for its cultures
on another continent too. The live tech tree (lane 192) runs per people, not per culture or polity.

If never done: the culinary timeline's dates for keeping methods (and the sheets' "not yet" lists at past eras) are early for a people's
far-flung cultures, and the "from whom" names a neighbour the culture never met. A book built on the timeline would date its salt fish or
cheese wrongly for those cultures.

Try: date a method per culture as the later of the people's date and the first frame at which the culture's land touches a culture of a
people that knew it then (contacts, or techspread's per-culture read-out), or record per-culture first-known dates in the live tree.
- [ ] two cultures of one people on different landmasses get different dates for a method learnt by contact

## Updates
- 2026-11-11: Created from inbox draft draft-keeping-dates-are-people-wide.md (found by lane309).
