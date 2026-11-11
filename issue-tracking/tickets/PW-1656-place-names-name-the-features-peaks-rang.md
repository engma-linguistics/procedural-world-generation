---
id: PW-1656
title: "Place names: name the features (peaks, ranges, capes, bays, islands, lakes, regions); rivers keep names longest, towns are renamed most"
type: story
status: todo
parent: PW-1736
milestone: v4
subsystem: culture
effort: m
impact: high
found_by: coordinator
blocked_by: []
relates: [PW-972]
refs: [planet/language/names.py]
created: 2026-11-10
updated: 2026-11-11
---

## Description
In plain words: towns and the biggest rivers get names now; mountains, capes, bays, islands and regions mostly don't. Name them with each family's habits (PW-1658), and make names last as long as real ones do: river names are the oldest layer (Europe's river names predate most of its languages; Mississippi is Ojibwe 'great river'), mountains next, towns least. Conquest and resettlement rename towns often, rivers rarely; a newcomer more often keeps a river's old name as heard (P2, already done for rivers) and adds its own word for 'river' on top (River Avon, Pendle Hill = hill-hill-hill: the tautology flag exists).

Acceptance: every named feature carries its namer, age and layer; on a24559 the median age of river names exceeds mountains', which exceeds towns'.

## Updates
- 2026-11-10: Created from inbox draft draft-name-features-and-durability.md (found by coordinator).

## From lane 15 (folded draft: feature names follow family habits)
In plain words: lane 15 gave each language family its own way of naming towns (generic last and worn to an ending,
generic first, 'X of the Y', 'X's place', a locative prefix; a24559: same-family habits overlap 0.95, other families 0.23).
Rivers, lakes, seas and peaks are still named the old way everywhere: water or mountain word + an adjective, in the
grammar's compound order (`water_name`, `plain_place`). So a Japanese-like family names its towns -yama / -kawa style but
its river is still 'red river' in plain compound order, an Arabic-like family has no 'Wadi X' or 'Jabal X' river or peak,
and two families' river lists look the same. What misleads if never done: the map's biggest labels (rivers, peaks, seas)
do not show the family difference the settlements now show.

Try: let `water_name` and `plain_place` take the namer's habit (`Habits.habit(namer)`): its order (generic first or
last), its article (construct), rendaku (feature), the locative prefix (locative), and the habit's river / hill generics
as the head (VALLEY for a construct river, MOUNTAIN for a feature peak). Keep the English Common rendering as is.
- [ ] a24559: river and peak names of two families with different templates told apart by eye
- [ ] tests: a construct habit names a river 'generic + article + specific'
- 2026-11-11: Moved under the language finish-line epic PW-1736 (assessment docs/review/language/assessment-2026-11-11.html; owner agreed 11-11).
