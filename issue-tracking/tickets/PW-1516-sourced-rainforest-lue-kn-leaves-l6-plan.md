---
id: PW-1516
title: "Sourced rainforest LUE/KN leaves L6 planets ~0.8 C warmer late with no weathering factor moved: find the path"
type: task
status: wontdo
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
- 2026-11-08: Status todo -> wontdo. Coordinator 11-08: closed as chaos (scout 217). Every plant-to-CO2 path flat; the volcanic source (tectonic, seeded drift) moved +2.8%, enough for +0.05-0.1 e-folds. scout2b_mech.py now prints CO2 vs source/sink so the next paired plant judge checks it directly.
- 2026-11-08: Scout 217 (pass 1, docs/review/climate/npp/scout3.md section 6): enumerated every plant -> CO2 path in the code (co2_stock settles at sink x co2_law = source): rooted cover -> w_plant, ground cover -> erosion supply, woody/deep cover and leaf albedo -> runoff and temperature -> w_q/w_temp, the spin-up references, methane (reads dT and runoff only); NPP itself is not read since PW-1424 C. All flat in 210b's mech.txt; w_temp leans up, which would lower CO2, not raise it. The input that moved is the volcanic source (source_raw +74 [-2, +263], 23/36 up): ridges + arcs + plumes x a per-step seeded drift, reachable by the plants only through the runs' chaotic divergence; +2.8% source needs about the +0.05-0.1 e-folds seen. Verdict: chaos; lean close. Not fully proven because 210b's runs are deleted; scout2b_mech.py now prints the per-pair r of d late CO2 against d ln source_raw / sink_raw / w_*, so the next paired judge of a plant change settles it directly.
- 2026-11-08: Created from inbox draft draft-rainforest-lue-warm-shift.md (found by scout210b).
