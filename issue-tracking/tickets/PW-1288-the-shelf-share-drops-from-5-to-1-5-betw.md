---
id: PW-1288
title: The shelf share drops from ~5% to ~1.5% between 100 and 150 Myr, then only slowly recovers
type: task
status: todo
parent: null
milestone: null
subsystem: surface
effort: m
impact: med
found_by: lane-100c
blocked_by: []
relates: [PW-950]
refs: [docs/review/tectonics/margin/margindiag.py, docs/review/tectonics/margin/report.md]
created: 2026-11-01
updated: 2026-11-01
---

## Description
In plain words: early in a run the continents have shelves about as wide as Earth's. Within the next 50 Myr most of
that shelf is gone, and afterwards it only slowly grows back to about half of Earth's. That points at something in the
first 150 Myr that removes the shelves (the start-up continents' shelves drowning or eroding off), not a slow narrowing
with age.

Numbers (L6, 36 paired-judge draws, median of the per-draw means of margindiag's shelf %, 0 to -200 m, of the ocean):
main 4.96 at 100 Myr, 1.31 over 150-250, 1.63 over 300-500, 2.31 over 550-750, 2.72 over 800-1000 Myr. With
`neck_km=200 rise=1 slope_k=1000`: 4.55, 1.69, 1.96, 2.42, 2.70. Earth on L6 is 6.2%. In the seed-1 and seed-3 screens
the drop is in every arm, between the 100 and the 150 Myr samples. The coordinator's L8 1 Gyr world (run 6a6fd6) has
0.64-1.17% against 4.18% in the L8 100 Myr world a16f5a (gyr-notes.md). Sea-floor creep doesn't change this.

What to try: record the shelf share every 10 Myr over 0-200 Myr at L6, plus the sea level, the submerged continental
area and the shelf cells' sediment budget (river supply against creep and erosion), to see what removes the start-up
shelves. Then see why the margin builds new shelf so slowly (river supply to the coast? the fill-to-SHELF_TOP rule?).
Lane 100d (docs/review/tectonics/margin/diagnosis-land.md part 4; a 2 Myr trace of draw 819014, plus all 36 main
draws): the 100 Myr "shelf" is the start-up continents' low plain, flooded by the ridge highstand (+235 m at 100 Myr).
It goes in the start-up continents' first assembly. From 100 to 150 Myr the continental area falls 2.9 points (36/36
draws) and the mean continental crust thickens 2.2 km (36/36). Collision and overlap lift and squeeze the flooded
plains, and in 18/36 draws the sea also falls more than 100 m. In 819014 the sea barely moves (243 to 206 m) while
the shelf goes from 5.2 to 1.0%. It is not rifting, erosion, isostasy or the brink rule, and it isn't a bug. The slow
recovery after it is the built margin (PW-950 itself). Related: PW-1230 (the early highstand).
- [x] the cause of the 100-150 Myr drop named, with numbers
- [ ] decide whether the start-up layout (assembly within ~100 Myr) or the start-up highstand needs changing, or close

## Updates
- 2026-11-01: Created from inbox draft draft-l6-shelf-collapses-after-100-myr.md (found by lane-100c).
