---
id: PW-1451
title: A polity keeps its founders' people in its name and card after another people holds its capital
type: task
status: todo
parent: null
milestone: v3
subsystem: peoples
effort: s
impact: med
found_by: lane177
blocked_by: []
relates: [PW-1431, PW-1433]
refs: ["planet/lineages/polities.py::_new_record", "planet/lineages/polities.py::derive", "planet/lineages/polities.py::_name", "viewer/globe/polities.js::polityRows", "run 3c1caf", planet/lineages/invasions.py]
created: 2026-11-04
updated: 2026-11-04
---

## Description
In plain words: on 3c1caf the three biggest "cervid-folk" polities ("South-east of Razukum (cervid-folk)", its 2 and 3) were
ruled by a human culture (`human:founding:198.000:-9.8:133.8`) from 6.2, 4.7 and 4.2 kyr ago, while they were states and empires
(5.2-3.4 kyr ago). The town's holder changed, and the seat's people with it, but the record keeps `people` (and so its name and the
card's "a town of the cervid-folk") from the first seat (`_new_record`). Found while checking invasions you schedule (PW-1433): a row
"the cervid-kin come down on the humans" correctly finds no cervid state, yet the globe shows three "cervid-folk" empires then.

What misleads if never done: Daniel reads a state as cervid-kin when humans ruled it, and his invasion read-out ("no state of the
cervid-kin existed then") seems to contradict the map.

What I'd try: when a record's ruling people changes (its `rulers` already track the culture), either start a new record (a new
dynasty of another people) or keep `people` per tier span and name the polity by its ruling people at its peak.
- [ ] a polity's name and card name the people ruling it then

## Updates
- 2026-11-04: Coordinator: milestone v3; the map should name the ruling people so it agrees with the invasion read-out.
- 2026-11-04: Created from inbox draft draft-polity-named-for-founders-not-rulers.md (found by lane177).
