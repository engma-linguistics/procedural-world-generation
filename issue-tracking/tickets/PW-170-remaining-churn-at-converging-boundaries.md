---
id: PW-170
title: "Remaining churn at converging boundaries: plate ownership flickers along collision fronts"
type: task
status: todo
parent: null
subsystem: tectonics
effort: m
impact: med
found_by: tectchurn
blocked_by: []
relates: [PW-108]
refs: [planet/tectonics/plate_kernels.py, tools/churn.py, "run:abcdac", "run:11ca32"]
created: 2026-10-14
updated: 2026-10-15
---

## Description
After PW-108's fix, churn near converging boundaries is halved but not gone
(`tools/churn.py`, share of continental cells within 3 cells of a converging
boundary that flip and flip back within 8 Myr): L7 s21 any_conv 12.9 -> 6.7%,
of which plate_conv (owner p -> q -> p) is unchanged at ~2.0-2.3%, crust_conv
4.1%, relief_conv 2.4%. L6 s21: any_conv 8.4 -> 4.3%, plate_conv 1.5 -> 1.1%.
Owner flips: `resolve` gives a continent-continent cell to its previous owner,
deletes the loser's sampled cell and stacks its thickness; the loser's
unsampled cells survive as ghosts within a cell of the front
(`cleanup_ghosts` only removes 'deep' ones) and win cells back when the front
wobbles; gaps behind a wobbling front become new ocean floor (age 0) inside
the belt (seen in run 428083, cell 110673: 5349 m, 68 km -> oceanic, 19 km,
age 2 within 4 Myr). Try: delete a ghost wherever it would lose to the cell's
owner by resolve's rules (stacking continental ghosts onto the winner), and
fill gaps whose plates don't diverge from the neighbours (see the draft on
spurious new floor).

## Updates
- 2026-10-15: Merged inbox draft draft-collision-ghosts-tried.md ("Collision-front owner flicker: deleting losing ghosts at the front didn't help", found by tectfound).
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
- 2026-10-14: Created from inbox draft draft-collision-owner-flicker.md (found by tectchurn).
