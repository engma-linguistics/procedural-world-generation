---
id: PW-1516
title: "Sourced rainforest LUE/KN leaves L6 planets ~0.8 C warmer late with no weathering factor moved: find the path"
type: task
status: todo
parent: null
milestone: later
subsystem: climate
effort: s
impact: low
found_by: scout210b
blocked_by: []
relates: [PW-1331]
refs: [docs/review/climate/npp/scout2.md, docs/review/climate/npp/scout2b/mech.txt, docs/review/climate/npp/scout2b_mech.py, docs/review/climate/npp/scout2b/stats.txt, "planet/tectonics/earth.py::weathering", "planet/vegetation.py::KN_RESP", "exports/s210b/judge (scout 210b's worktree, scratch)"]
created: 2026-11-08
updated: 2026-11-08
---

## Description
**In plain words.** Pass 2's 36-planet judge of the sourced rainforest numbers (KN_RESP 0.15, TrBE eps 1.43) passed,
but the planets' late climate came out a little warmer than on main (same 36 draws): median paired late dT +0.77 C
(CI of the median [-0.26, +1.87]; of the mean [+0.03, +1.55]), carried by a higher late CO2 (+0.10 e-folds,
[+0.02, +0.22], 24 of 36 up). The hot-desert share grows with that warmth (+0.95 points of land), as main's own planets
do per degree. None of the weathering's logged factors (w_plant, w_bare, w_temp, w_supply, w_area, the references)
moves beyond chance, so the path from more rainforest growth to more CO2 is not known. It may be chaos at the edge of
the interval.

What misleads if never done: a later plant change could add another unexplained warm step, and nobody would know
which part of the carbon cycle carries plant growth into CO2.

- [ ] list where NPP (not rooted cover) still enters the carbon cycle or the climate (soil CO2, litter, organic
  burial, albedo of leaf area) and log it in the diag if missing
- [ ] if a path exists, check its size against the +0.10 e-fold; otherwise close as chaos

## Updates
- 2026-11-08: Created from inbox draft draft-rainforest-lue-warm-shift.md (found by scout210b).
