---
id: PW-1464
title: "Tech tree: arms B and E need the town footprint before the tree is built"
type: task
status: todo
parent: null
milestone: later
subsystem: culture
effort: m
impact: med
found_by: lane-186
blocked_by: []
relates: [PW-1461]
refs: ["planet/lineages/techtree.py::build", "planet/lineages/techtree.py::rebuild", "planet/lineages/techspread.py::town_footprint", "planet/lineages/output.py::save", planet/lineages/settlements.py, docs/review/culture/writing/round2.md]
created: 2026-11-04
updated: 2026-11-04
---

## Description
**In plain words.** Two of D52's ways to speed writing between town-dwelling peoples, B (writing crosses a people's towns, not its
whole land) and E (a court takes writing when its nearest town touches a writer), need to know where each people's towns are. The
tech tree is built first in `output.save`, and the settlement ledger (where the towns are) is built from the tech tree afterwards.
So today B and E work only when a stored run's tree is rebuilt (`techtree.rebuild` reads the ledger). If Daniel picks B or E for
D52 and this is never done, new peoples runs cannot use it: a tree file that turns B or E on gets a warning and the plain rule.

What to try: build the tree, then the ledger, then rebuild the tree with `techspread.town_footprint` and the ledger once more (the
ledger reads only towns, villages, roads, mines, copper, iron, delving and fortifications from the tree; check whether any of those
can change when writing moves, and stop after the second pass if not). It costs one more ledger build (~25 s on 07c755).

Only worth doing once D52 is ruled for B or E (lane 186's round2.md has the measures).
- [ ] a new peoples run with `contact_arms = "E"` (or B) gets the same tree as `techtree.rebuild` of it
- [ ] the warning in `techtree.build` never fires in `output.save`

## Updates
- 2026-11-04: Created from inbox draft draft-techtree-town-arms-need-the-ledger-first.md (found by lane-186).
