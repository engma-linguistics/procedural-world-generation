---
title: "Place names: rivers, lakes and peaks still ignore the family's naming habit (only settlements follow it)"
type: task
status: todo
parent: PW-767
milestone: v4
subsystem: culture
effort: s
impact: med
found_by: lang-lane15
blocked_by: []
relates: [PW-1658, PW-1654]
refs: [planet/language/placenames.py::Habits, planet/language/names.py::_Pass.water_name, planet/language/names.py::_Pass.plain_place, "scratch pass a24559 (lane 15)"]
---

## Description
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
