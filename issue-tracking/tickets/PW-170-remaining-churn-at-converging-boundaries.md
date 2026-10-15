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
updated: 2026-10-14
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
- 2026-10-14: Created from inbox draft draft-collision-owner-flicker.md (found by tectchurn).
