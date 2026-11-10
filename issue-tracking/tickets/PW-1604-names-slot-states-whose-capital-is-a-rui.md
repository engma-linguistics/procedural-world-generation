---
id: PW-1604
title: "Names slot: states whose capital is a ruin keep a gloss name; the languages name only living settlements"
type: task
status: done
parent: null
milestone: v5
subsystem: culture
effort: s
impact: low
found_by: lane255
blocked_by: []
relates: [PW-1436, PW-972, PW-1435]
refs: ["planet/lineages/nameslot.py::apply_polities", "planet/lineages/nameslot.py::place_names", "planet/language/names.py::build_names", "run:a24559", "run:1e97dd"]
created: 2026-11-09
updated: 2026-11-10
---

## Description
In plain words: the names slot (PW-1436) names a state after its capital town in the run's languages, for example "Uguhubju
(humans)". The languages pass (languages.json `names.demes[d].settlements`) only names settlements that are alive now. A state
whose capital has since been abandoned therefore keeps the old gloss name, such as "West of Simath (gnomes) 167". So do the
calendars counted from it, such as "the Founding of the west of Simath II". Most states in the run fell long ago, so most of
them keep gloss names even on runs that have languages (a24559, 1e97dd). If this is never done, old states and their calendars
stay numbered repeats of a region's name, while living towns have real names.

Fix in the languages pass: also name the ruins and abandoned capitals (in the lect of the people who held them, at the time
they were abandoned), and list them in `settlements` with their `site`. The slot already reads any site there.

## Updates
- 2026-11-10: Status todo -> done. Lane 11 (lang-lane11), language side done: names.build lists every abandoned site but mines (personal.Personal.ruins: about 14k on a24559), named in the lect of the last holders' deme on the cell when it was left (else the founders'), kind 'ruin' with abandoned_kyr, under the deme whose lect named it (a gone deme gets an entry marked gone). a24559 with polities.derive: all 4,352 states with a ruined capital now resolve to a name; named capitals 1,848 -> 6,200 of 15,013. The polities side needs nothing: nameslot.place_names already reads every settlements entry by site; re-run the slot after a languages pass. Left: 8,618 states whose living capital is not among its deme's 3 biggest places (SITES_PER_DEME): inbox draft, v5.
- 2026-11-09: Created from inbox draft draft-names-for-old-capitals.md (found by lane255).
