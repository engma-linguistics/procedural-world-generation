---
id: PW-1262
title: "A real L9 world, measured: 1.76 GB of JSON, 38 min and 39 GB to make by refining an L7 world"
type: task
status: todo
parent: PW-1198
milestone: later
subsystem: store
effort: xs
impact: med
found_by: lane104-refine-l8
blocked_by: []
relates: [PW-1209, PW-490]
refs: [planet/refine.py, docs/review/refine-l8/design.md]
created: 2026-11-01
updated: 2026-11-03
---

## Description
**In plain words.** Lane 104 made a real L9 world (2.6 million cells of ~15 km) by refining the L7 world 783674. It
took 38 minutes and 39 GB of memory. The file is 1.76 GB of JSON (229 MB gzipped) plus a 370 MB L9 grid file. That
is 3.3 times Chrome's longest string (537 M characters), so the viewer cannot open it, as PW-1209 predicted. The
world was deleted after measuring (it was a scratch store).

Evidence for PW-1209 (binary world layers), which this should be merged into: the L9 target is now a measured
1.76 G characters, not an estimate, and the grid file (370 MB of JSON) needs the same binary treatment as the layers.
- [ ] fold into PW-1209's acceptance: an L9 refined world (`planet refine <world> --level 9`) opens

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: L8/L9 whole-world work, post-v2 (see PW-1198 space-to-ground globe)
- 2026-11-01: Created from inbox draft draft-l9-world-measured.md (found by lane104-refine-l8).
