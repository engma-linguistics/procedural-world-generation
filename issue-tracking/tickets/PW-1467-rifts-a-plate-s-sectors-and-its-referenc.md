---
id: PW-1467
title: "Rifts: a plate's sectors and its reference cells disagree by ~2x on a turned plate; check rift_side and the margin split too"
type: task
status: todo
parent: null
milestone: later
subsystem: tectonics
effort: s
impact: low
found_by: lane191
blocked_by: []
relates: [PW-1261]
refs: ["planet/tectonics/events.py::triple_split", "planet/tectonics/events.py::split", "planet/tectonics/events.py::sliver", "planet/tectonics/events.py::rift_side", tests/test_rifts.py]
created: 2026-11-04
updated: 2026-11-04
---

## Description
**In plain words.** When a plume cracks a plate (triple_split), the rule judged each piece by counting continent on the world cells of
its sector, but the split itself moves the plate's reference cells. On the L4 seed-1 run at 216 Myr the sector count gave a piece of
126 continental cells (allowed) while the split really moved 61 (a sliver, 0.0238 of the surface). Lane 191 (8b51c6d8) made
triple_split check the real pieces through w_ref, as the stress rift already did. Not understood: why the two counts differ ~2x on a
plate that has turned a lot, and whether rift_side or the margin split have the same gap.

What misleads if never done: other split paths may still let 1-3% continental slivers through, which the rift rule says can't exist.

- [ ] For the failing case, show where the sector labels and the reference-cell labels part ways (rotation, stale w_ref?).
- [ ] Check rift_side and the margin split for the same sector-vs-w_ref gap; add the w_ref check where missing.

## Updates
- 2026-11-04: Created from inbox draft draft-rift-sector-vs-refcell-gap.md (found by lane191).
