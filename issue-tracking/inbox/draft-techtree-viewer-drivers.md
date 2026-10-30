---
title: "Technology tab: show what drives each people's inventing (population, specialists, learners, culture)"
type: task
status: todo
parent: PW-913
subsystem: viewer
effort: s
impact: low
found_by: fun-lane-64
blocked_by: []
relates: [PW-913]
refs: [viewer/techtab.js, planet/lineages/techtree.py]
---

## Description
The v1 invention model writes `meta.techtree.drivers[line]`: population now, specialist share, the pool strengths (whole people and
specialists), generation and learners factor, kind rate_x, and the culture's factors per domain (invent and take). It also writes, per
tech, `domains`, `pool`, `floor_kyr` (a hard floor, or null for a soft tech), `rate` and `anchor_lag_kyr`. The Technology tab doesn't
show any of these yet. The owner uses the viewer, not the CLI, so a per-people line ("why the dwarves are slow: 1.8 M, 10%
specialists, x1.6 learners, craft x1.3") would make the unevenness readable.
- [ ] per-people drivers in the people view of the tab
- [ ] domains and soft or hard floor in the tech tooltip
