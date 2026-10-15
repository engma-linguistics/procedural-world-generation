---
id: PW-182
title: Showcase world a08983 (run 8571dd) still carries the old raw-precipitation dune classes
type: task
status: todo
parent: null
subsystem: surface
effort: xs
impact: low
found_by: zoompolish
blocked_by: []
relates: [PW-176]
refs: [planet/landform.py, "run 8571dd", "world a08983", "zoom:ee587f"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
PW-176 changed the dune-field rule to the aridity index (P / PET < 0.12,
`landform.aridity`). Landform classes are made during the run (keyframes),
and a world copies them, so run 8571dd and world a08983 keep the old
classes (dunes 5.6% of land, half of them cold) until the next showcase
run. A replay of 8571dd from its 400 Myr checkpoint to 408 Myr gives the
new shares: dunes 5.5% -> 3.0% of land, cells with mean T < 0 C among them
1544 -> 258 (the rest are genuine polar deserts at 20-40 mm/yr); hills
62.0 -> 64.7%, every other class unchanged. The zooms of the hot dune
demos (e14044, 2d1537) and the rift/escarpment demos (2d06f8, f9b027)
don't touch any cell that changes; the cold-erg zoom ee587f (59.3N) and 2
cells near a42a15 would lose their dunes.
- [ ] At the next showcase run (or the planned L8 + matching L7), check
  the dune share and that ee587f's area is no longer an erg.

## Updates
- 2026-10-14: Created from inbox draft draft-showcase-old-dune-classes.md (found by zoompolish).
