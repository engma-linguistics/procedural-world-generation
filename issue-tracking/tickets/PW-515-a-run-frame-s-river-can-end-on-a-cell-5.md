---
id: PW-515
title: A run frame's river can end on a cell 5 m above a neighbouring salt pan (test_frame_rivers_end_in_its_own_hollows)
type: task
status: todo
parent: PW-470
milestone: v2
subsystem: hydrology
effort: s
impact: low
found_by: pw465
blocked_by: []
relates: [PW-465, PW-461]
refs: [tests/test_health.py, planet/hydrology.py]
created: 2026-10-21
updated: 2026-10-21
---

## Description
`tests/test_health.py::test_frame_rivers_end_in_its_own_hollows` fails on the PW-465 side-lane branch
(and failed on PW-461's a2 code too), though neither touches hydrology: the changed ice changes the
run's trajectory and exposes the case. L4 run (helpers.run_sim), t = 220 Myr: cell 2461 (38.2 N, 415 m,
no ice, no lake, downstream -1) is a drainage end, but `real_hollows` doesn't count it. Its neighbours
are 410 m (a SALT_PAN cell) and 569-893 m. So the end sits on the rim of a salt pan, 5 m above it,
and doesn't drain into it. Likely the pan's routing (or the filled surface) and the frame's raw
elevation disagree by a few metres at a pan's edge. Passes on main today.
- [ ] a drainage end beside a lower salt pan drains into it (or the check counts the pan's rim)
- [ ] the test passes on the PW-465 branch

## Updates
- 2026-10-21: Created from inbox draft draft-river-end-beside-salt-pan.md (found by pw465).
