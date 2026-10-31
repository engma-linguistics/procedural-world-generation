---
id: PW-1228
title: 3D relief draws a regular lattice of diamond-shaped dimples over shallow seas (L8 world a16f5a)
type: task
status: todo
parent: null
milestone: later
subsystem: viewer
effort: s
impact: low
found_by: lane96
blocked_by: []
relates: []
refs: [viewer/relief.js, "world a16f5a", docs/review/l8-world/explore/02_spot_step_relief.jpg]
created: 2026-10-31
updated: 2026-10-31
---

## Description
In plain words: with "3D relief" on, the flooded shelf east of Ratote (lat -27, lon -88) is covered in evenly spaced
little diamond dents, like a quilted pattern. The data has no such pattern, so it is the drawing, not the planet.

Seen at `?world=a16f5a.json&layer=elevation&view=-26,-86&dist=1.45&relief3d=1&ex=10` (screenshot
docs/review/l8-world/explore/02_spot_step_relief.jpg). The shallow continental sea there is -150..+5 m with
cell-to-cell noise; single-cell dips are small (in a16f5a's shallow continental seas 1,092 one-cell pits, median 4 m
deep, p90 26 m) and not on a lattice. The dimples are regularly spaced every few cells, so likely the sea-floor
mesh (vertex sharing or the translucent sea plane meeting floor vertices near 0 m) rather than the elevations.
Not checked at L7 (it has almost no shallow sea to show it).

## Updates
- 2026-10-31: Created from inbox draft draft-3d-relief-diamond-lattice-on-shallow-seas.md (found by lane96).
