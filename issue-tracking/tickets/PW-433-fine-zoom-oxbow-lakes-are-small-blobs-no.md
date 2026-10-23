---
id: PW-433
title: Fine zoom oxbow lakes are small blobs; no scroll bars or meander scars on the floor
type: task
status: todo
parent: PW-649
milestone: later
subsystem: zoom
effort: m
impact: low
found_by: pw425
blocked_by: []
relates: [PW-425, PW-416, PW-412]
refs: [planet/zoom_fine_meander.py, planet/zoom_fine.py]
created: 2026-10-16
updated: 2026-10-23
---

## Description
PW-425 cuts off some of the biggest loops (planet-fixed, `zoom_fine_meander.CUT_OM` / `CUT_P`). The river then runs a smaller bend there, and the old loop's apex arc becomes an oxbow lake: a shallow pool on the valley floor (`zoom_fine.build`, step 4b). In practice they come out as a few small blobs (352c76: 0.013 km2, 2 lakes in 47 km of meanders). Only the parts of the arc that stand a channel width plus 2 px clear of the new channel are kept, and those are short at w/res ~3. The floor also shows no scroll bars (ridge and swale on a bend's inside) and no older meander scars.

What I'd try:
- draw the whole old loop and route the new channel through its neck, rather than shrinking the bend in place. That gives proper crescents.
- add older scars as faint, partly filled swales (a few dm deep) on the belt, from the same train at earlier phases. PW-416 (migration over time) gives these for free, so maybe do this as part of PW-416.
- scroll bars: low arcs concentric with each bend's inner bank, inside the belt.
- [ ] oxbows read as crescents in a 25 m zoom of a 300 m^3/s river
- [ ] block means (PW-389) and floor tests unchanged

## Updates
- 2026-10-23: Filed under the quality-pass epic PW-649 (parent PW-649, milestone later): shipped and judged good enough, residual kept for a later cleanup pass.
- 2026-10-16: Created from inbox draft draft-oxbow-crescents-and-scroll-bars.md (found by pw425).
