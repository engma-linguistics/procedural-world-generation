---
id: PW-1527
title: "Should a religiously tolerant culture also take its neighbours' faith more readily? (today it does: the two effects cancel on minorities)"
type: task
status: done
parent: null
milestone: null
subsystem: culture
effort: s
impact: med
found_by: lane219
blocked_by: []
relates: [PW-1477, PW-1489]
refs: ["planet/lineages/gods.py::RECEPT_MID", "planet/lineages/gods.py::Pantheons._links", "planet/lineages/gods.py::Pantheons._pulls", planet/lineages/attitudes.py, docs/review/culture/faiths/tolerance1.md, docs/review/culture/attitudes/round1.md]
created: 2026-11-08
updated: 2026-11-08
---

## Description
In plain words: since PW-1477 a culture's tolerance does two things to faiths. A tolerant culture absorbs its own minorities slowly (they persist),
and it also *takes a neighbour's faith more readily* (receptiveness = tolerance / RECEPT_MID, 0..2). Lane 219 moved both onto the new religious
tolerance. On 0141d1, 3e0eb4 and 07c755 (six re-rolled draws each) the most religiously tolerant third of cultures carries about the same
minority share as the least tolerant third (4.9 against 4.0 %, 3.2 against 3.1 %, 4.6 against 5.3 %): the two effects cancel.

Options:
- A. Keep it (lean): open-minded peoples do convert more readily (the Mongol khans took their subjects' faiths); the tolerance shows in persistence and in plural realms, not in larger minorities.
- B. Receptiveness reads the tolerance *of outsiders* and religious tolerance only sets the push and the persistence: a tolerant faith-community keeps its own and lets others be. Minorities would then grow with tolerance; conversions by neighbours would no longer follow religious tolerance.
- C. Receptiveness is fixed at 1 (no tolerance term): simplest, and drops a judgement.

What misleads if never decided: Daniel's "tolerant rulers let faiths mix" does not show in the per-culture minority numbers, and a reader of the viewer may take it for a bug.

## Updates
- 2026-11-08: Status needs-decision -> done. Daniel ruled D70 A 11-08: keep both as built (religious tolerance shields minorities; town-borne minorities). Regional pantheons (D68) add polytheist mixing on top.
- 2026-11-08: Desk D70 (lean A).
- 2026-11-08: Created from inbox draft draft-religious-tolerance-receptiveness.md (found by lane219).
