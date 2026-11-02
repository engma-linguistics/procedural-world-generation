---
id: PW-1295
title: With the sea-floor creep, the continents' outer cells flicker between continent and ocean floor at the 20 km bound
type: task
status: todo
parent: null
milestone: null
subsystem: tectonics
effort: m
impact: med
found_by: lane-112
blocked_by: []
relates: [PW-1292, PW-950, PW-108]
refs: [planet/tectonics/crust.py, docs/review/tectonics/margin/pw1292-note.md, docs/review/tectonics/margin/tracediag.py]
created: 2026-11-01
updated: 2026-11-01
---

## Description
In plain words: with the sea-floor creep on, the model keeps turning the continents' outermost cells into ocean floor
and back again. The churn PW-1292 was opened for (+45 000 born, -40 000 shredded per 400 Myr) is mostly this, not
isolated sediment piles. Turning isolated piles to ocean floor (PW-1292 option A) changed it by 0-14%.

Numbers (L6, seeds 1 and 3, 600-1000 Myr, tracediag.py `births`, docs/review/tectonics/margin/pw1292-note.md): with
`neck_km=200 rise=1 slope_k=1000`, coherence shreds 3300-3800 cells against 1100-1300 on main. Only 660-840 of them
are pile rock. Births of crust that is mostly basement (classed "arc") double, 990-1060 against 410-430, though no
arc process doubles. Requiring 3 continental neighbours for a pile's birth (screen `pile_touch=3`) didn't reduce the
churn and ran 4-5 C colder on both seeds.

Likely cause (not yet proven): the birth bound and the shred bound are the same 20 km (`BECOMES_CONT_KM`). Necking
and the creep stripping the cover leave the margin's outer cells near 20 km. Below it, with at most 2 continental
neighbours, a cell is shredded and keeps its thickness. When sediment or crust flow brings it back to 20 km, it is
born again.

What to try:
- [ ] tag the shredded cells in tracediag.py and count how many are born again within 50 Myr (confirms or rules out the flicker)
- [ ] if confirmed, screen hysteresis between the bounds (a shred only below ~15 km, or re-birth of a shredded cell only above ~25 km), on seeds 1 and 3 with the creep
- [ ] then a paired judge of the creep on top of it (judge 2 in deep-dive.md failed with 2 frozen-over worlds)

## Updates
- 2026-11-01: Created from inbox draft draft-margin-cells-flicker-at-the-20-km-bound.md (found by lane-112).
