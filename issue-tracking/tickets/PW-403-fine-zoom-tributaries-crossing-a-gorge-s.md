---
id: PW-403
title: Fine zoom tributaries crossing a gorge's walls keep their plateau beds
type: task
status: todo
parent: null
milestone: null
subsystem: zoom
effort: s
impact: low
found_by: pw390-fine-zoom-gorge
blocked_by: []
relates: [PW-129, PW-390]
refs: [planet/zoom/fine.py, "zoom 3e74b0", "zoom b3c260"]
created: 2026-10-16
updated: 2026-10-16
---

## Description
A parent tributary that joins the river inside a fall's gorge is imposed as a course with the
parent's bed, which is at plateau height until the parent's own confluence node. The gorge's walls
are cut round it (courses are excluded from the cut), so it crosses the wall as a 1-px rib at the
rim's height and then drops to the floor unlisted (3e74b0: a course at ~1590 m beside walls cut to
~730 m, 1.9 km below the 822 m fall). A hanging valley is right for a tributary of a gorge, but it
should end at the rim with its own (listed) fall, not run as a rib down the wall.

What I'd try: in zoom_fine step 4, end such a course at the gorge's rim (its pixels inside the cut
become wall), list the drop from its rim pixel to the floor as a fall (kind "hanging"), and route
its water over it.
- [ ] no course pixel inside a gorge's walls stands more than 50 m above the walls beside it

## Updates
- 2026-10-16: Created from inbox draft draft-fine-zoom-hanging-tributaries.md (found by pw390-fine-zoom-gorge).
- 2026-10-30: planet/zoom.py and planet/zoom_*.py moved into planet/zoom/ (regional.py, fine.py, ...) and zoom.build split into named stages (stage_*.py), lane 55; the file names here are the new ones, but the line numbers in the text are from before the move.
