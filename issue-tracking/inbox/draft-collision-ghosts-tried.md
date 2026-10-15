---
title: "Collision-front owner flicker: deleting losing ghosts at the front didn't help"
type: task
status: todo
parent: null
subsystem: tectonics
effort: m
impact: low
found_by: tectfound
blocked_by: []
relates: [PW-170]
refs: [planet/tectonics/plate_kernels.py, tools/churn.py]
---

## Description
Findings for PW-170 (merge into it). Tried the ticket's suggestion in
`plate_kernels.cleanup_ghosts`: a plate's ref cell lying in a world cell
another plate owns, next to cells of its own plate (a ghost at the front),
was deleted wherever resolve's rules say it loses (ocean under continent or
under younger floor; continent under continent stacked onto the owner).
L6 seed 21, 600 Myr, `tools/churn.py`: plate_conv 1.96% -> 2.35%, any_conv
4.10 -> 4.55%, spike 0.29 -> 0.35% (one seed each; the runs diverge, so
within noise), i.e. no gain, so it was reverted. Next idea: the flicker may
come less from ghosts than from resolve's continent-vs-continent rule
(previous owner wins) when the front's cells are resampled each step; log
which branch hands a cell to the other plate and back before changing more.
