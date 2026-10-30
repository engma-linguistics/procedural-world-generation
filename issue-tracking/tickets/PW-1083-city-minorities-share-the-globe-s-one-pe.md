---
id: PW-1083
title: City minorities share the globe's one "peoples overlay" slot with half-elves and tieflings; give them a layer of their own
type: task
status: todo
parent: PW-856
milestone: v2
subsystem: viewer
effort: s
impact: low
found_by: fun-lane-54
blocked_by: []
relates: [PW-889, PW-752]
refs: [viewer/globe/layers.js, planet/lineages/history/frame.py, planet/lineages/history/cities.py]
created: 2026-10-30
updated: 2026-10-30
---

## Description
In plain words. The globe shows a people that lives inside other peoples' land (half-elves, half-orcs, tieflings, and now the city
goblins and city kobolds) on one layer, "peoples overlay", and it can only show one of them per cell. Where the tieflings and the city
goblins both live in a human town, only one is drawn: the older line wins a tie. So the owner cannot see all of a town's minorities
at once on the globe. The peoples table in the lineages page does list them all, with their numbers.

What to try: store a per-cell bit mask, or a small "minorities" layer, holding every overlay present above EST in the frame
(history/frame.py), and draw it as a stack of coloured dots or a list in the cell's description, in the globe's peoples group.
- [ ] a cell description lists every minority there, with its share of the townsfolk
- [ ] a layer (or a toggle on "peoples overlay") shows city minorities on their own

## Updates
- 2026-10-30: Created from inbox draft draft-city-minorities-own-globe-layer.md (found by fun-lane-54).
