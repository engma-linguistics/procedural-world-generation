---
title: "Dormant arc volcanoes: the run has no state between active and extinct for arcs"
type: task
status: needs-decision
parent: null
subsystem: tectonics
effort: s
impact: low
found_by: volcano-highlights
blocked_by: []
relates: [PW-001, PW-116]
refs: [planet/zoom_volcanoes.py, planet/tectonics/volcanism.py, viewer/index.html, "run a1d3b9"]
---

## Description
The owner asked for dormant volcanoes. `zoom_volcanoes.status` now gives each volcano of the table
active / dormant / extinct: active is the run's flag; dormant is a hotspot vent carried off its plume but
still within the plume's head (`PLUME_KM`, 150 km), so it can erupt again (Haleakala, Yellowstone's older
calderas); everything else is extinct. On a world sliced from run a1d3b9 at 380 Myr (L7, seed 3199) that is 737 active,
4 dormant, 1666 extinct: dormant ones are rare, because a plume has one or two vents within 150 km.

Arc volcanoes have no dormant state: the run keeps each one "active" for its whole ~8 Myr life
(`volcano_life`) and extinct after, with no eruptions inside it, so it can't tell a cone that erupted
last year from one quiet for 50,000 years. Options:
- A. Keep it (lean): active / extinct for arcs is all the run knows; say so in the viewer (done).
- B. Call an extinct arc cone still within `volcano_spacing` (~120 km) of an active one on the same arc
  "dormant": the arc's slab still melts under it. Cheap, but on Earth such cones are mostly extinct (the
  Cascades' dead centres), so it would mislabel.
- C. Give arc volcanoes an eruptive life cycle in the run (repose intervals drawn per volcano, e.g.
  10^2-10^5 yr, and a "last eruption" age at the world's moment): dormant = active centre in a long repose.
  The run's Myr steps can't resolve it, so it would be a per-volcano random draw at slicing time, a
  made-up state, not physics.
