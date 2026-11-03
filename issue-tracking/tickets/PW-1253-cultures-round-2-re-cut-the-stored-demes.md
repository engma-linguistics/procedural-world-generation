---
id: PW-1253
title: "Cultures round 2: re-cut the stored demes of the dnd runs so the viewer shows the reach-scaled demes"
type: task
status: todo
parent: PW-670
milestone: null
subsystem: culture
effort: xs
impact: med
found_by: lane108
blocked_by: []
relates: [PW-670, PW-981, PW-1251]
refs: [planet/lineages/demes.py, "runs cc22df 622c00 (protected)"]
created: 2026-11-01
updated: 2026-11-01
---

## Description
In plain words: the demes now follow each kind's own reach (dragons and giants 1,500 km over land and sea, seafarers with
their boats). A run keeps the demes it was cut with, and the viewer works cultures out from those. Daniel's dnd runs cc22df
and 622c00 still hold the old demes, so the Cultures tab shows the new rules on the old demes (cc22df: 349 cultures, 126
alive, against 336 and 130 with the new demes). Lane 108 could not re-cut them because they are protected.

Fix: on main after the merge, run `uv run python -m planet demes cc22df 622c00` (about 12 s each). Then, optionally, run
`planet cultures cc22df 622c00` to store cultures.json. This rewrites demes.json, layers/demes.bin and meta.demes in the
protected runs, so it needs the coordinator's say. Settlements do not read the demes and are unaffected.
- [ ] demes re-cut on the dnd runs (or left as they are, with a note)

## Updates
- 2026-11-01: Created from inbox draft draft-cultures-recut-demes-on-owner-runs.md (found by lane108).
