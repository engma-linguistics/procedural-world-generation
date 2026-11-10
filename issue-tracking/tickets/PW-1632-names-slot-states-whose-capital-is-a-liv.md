---
id: PW-1632
title: "Names slot: states whose capital is a living village keep a gloss name (the languages name only each deme's 3 biggest places)"
type: task
status: todo
parent: PW-767
milestone: v5
subsystem: culture
effort: s
impact: med
found_by: lang-lane11
blocked_by: []
relates: [PW-1604, PW-1436]
refs: ["planet/language/personal.py::Personal.settlements", "planet/language/personal.py::SITES_PER_DEME", "planet/language/personal.py::Personal.ruins", "planet/language/names.py::_Pass", "planet/lineages/nameslot.py::place_names", "planet/lineages/nameslot.py::apply_polities", "planet/lineages/polities.py::derive", "run a24559"]
created: 2026-11-10
updated: 2026-11-10
---

## Description
In plain words: a state is named after its capital town when the languages pass has named that town. Lane 11 (PW-1604)
named the ruins, so states whose capital was abandoned now get real names. But most states on a24559 have a capital
that is still lived in, usually as a village, and the languages pass names only the three biggest living places of
each deme (`personal.SITES_PER_DEME = 3`). Those states keep gloss names ("West of Simath (gnomes) 167") and so do
the calendars counted from them. If this is never done, about 60% of the states in a run with languages keep
numbered gloss names, which is the thing PW-1436 set out to remove.

Numbers on a24559 (polities.derive on today's code, 15,013 states): before lane 11, 1,848 states had a named capital
(12%); after it, 6,200 (41%): all 4,352 states with a ruined capital are named now. Left: 8,618 states (57%) whose
capital is a living but unnamed place, and 195 with no capital site.

Options:
- A (languages side, my lean): name every living site that is or was a state's capital, beside the three biggest.
  The pass needs the capital site ids. a24559 has no polities.json, so either the languages pass derives polities
  (about 30-60 s; gods.derive already does it on old runs) or the names slot writes a small list of capital sites the
  languages pass reads. About 9k more names in languages.json (the ruins added about 2.7 MB for 14k entries).
  The ruins are named in the lect of their last holders when they were left; a capital the state's own people held
  at its peak but others held last is named in the later people's tongue. Naming capitals in the state's own
  people's lect at its peak would need the polity's people and peak time from the same list.
- B: name every living village (32k on a24559): simplest, but triples the names block and the names-pass time.
- C (names-slot side): fall back to the deme's own name for an unnamed capital ("the state of the Uguhubju"). Cheap,
  but every state of one deme then shares a name.

- [ ] most states with a living capital get a name from the languages on a24559 (or the share left is explained)

## Updates
- 2026-11-10: Created from inbox draft draft-living-capitals-unnamed.md (found by lang-lane11).
