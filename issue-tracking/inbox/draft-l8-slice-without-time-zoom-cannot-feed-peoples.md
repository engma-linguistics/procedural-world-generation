---
title: A world sliced straight from a run cannot start a peoples run (needs a time zoom); the error comes after a 14 min slice
type: task
status: todo
parent: null
subsystem: infra
effort: s
impact: low
found_by: lane-86b
blocked_by: []
relates: [PW-1143]
refs: [planet/lineages/recent.py, planet/make.py]
---

## Description
`planet lineages a16f5a` on an L8 world made by `planet slice 2c0c5d --at auto` fails with "world a16f5a was not finished from a time zoom"
(planet/lineages/recent.py `resolve`). Fine by design, but the user only learns it after the 14 min slice. `make` also stops at "slice" when the time zoom is skipped.
Say so in `lineages --help` and in the make form, or let lineages do a short time zoom itself. Also: the 300 kyr time zoom default is the expensive part at L8 (about 4 h); a
60 kyr zoom is what 86b used to get a present for the peoples run.
- [ ] help text or an early check in `lineages`
