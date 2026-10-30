---
id: PW-391
title: Fine zoom rivers can carry less water than the parent's
type: task
status: todo
parent: null
milestone: null
subsystem: zoom
effort: s
impact: low
found_by: pw129-fine-zoom
blocked_by: []
relates: [PW-129]
refs: [planet/zoom/fine.py, "zoom 3e74b0", "zoom b3c260", "zoom 97b3e7"]
created: 2026-10-16
updated: 2026-10-16
---

## Description
A fine zoom's discharge is local runoff plus the parent's discharge injected
where a parent river crosses into the built area: one injection per river,
at the first node of its course at least 2 px inside the region. At the
822 m fall (parent 97b3e7 at 100 m: 36 m3/s at the lip) the children carry
33.7 m3/s at 50 m (3e74b0) and 26.6 m3/s at 25 m (b3c260). Some
tributaries that enter the box seem to be skipped: the walk from the crossing
link to an in-region node gives up, or the river is skipped because a
re-entry check (`been_in`) catches it. The fall's listed discharge_m3s is
the parent's, so the stats are right, but the discharge layer and the river
widths aren't.

- [ ] log each entering river (parent q and where it was injected) and
      compare the children's discharge at the lip with the parent's
- [ ] within 10% of the parent's at the lip at 50 m and 25 m

## Updates
- 2026-10-16: Created from inbox draft draft-fine-zoom-inflow-accounting.md (found by pw129-fine-zoom).
- 2026-10-30: planet/zoom.py and planet/zoom_*.py moved into planet/zoom/ (regional.py, fine.py, ...) and zoom.build split into named stages (stage_*.py), lane 55; the file names here are the new ones, but the line numbers in the text are from before the move.
