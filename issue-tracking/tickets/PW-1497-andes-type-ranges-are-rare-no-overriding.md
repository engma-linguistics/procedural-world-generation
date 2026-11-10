---
id: PW-1497
title: "Andes-type ranges are rare: no overriding-plate shortening at ocean-continent trenches (runs 8-10% of land >3 km near such margins, Earth 25%)"
type: task
status: done
parent: null
milestone: v5
subsystem: tectonics
effort: l
impact: med
found_by: scout1-mountains
blocked_by: []
relates: []
refs: [docs/review/tectonics/mountains/scout1.md, docs/review/tectonics/mountains/scout9.md, docs/review/tectonics/mountains/scout9_decay.py, docs/review/tectonics/mountains/scout7_measure.py, "planet/tectonics/crust.py::andean_contraction", "planet/tectonics/crust.py::flow_and_orogeny", "planet/tectonics/plate_kernels.py::crust_flow", tools/fork_screen.py, tools/hard_bar.py, tools/judge.py, tools/scorecard.py, "Dewey 1988 Tectonics 7(6)", "Menard & Molnar 1988 Nature 334:235", "Braun & Robert 2005 ESPL 30:1203", "Baldwin, Whipple & Tucker 2003 JGR 108(B3)"]
created: 2026-11-07
updated: 2026-11-10
---

## Description
In plain words: on Earth a quarter of the land above 3 km is the central Andes, on an ocean-continent margin. In our runs only 8-10% of high ground is near such a margin, because the model only thickens crust at a trench by arc magmatism; it never shortens the overriding plate, so continent-continent collision is the only way to stack crust. See docs/review/tectonics/mountains/scout1.md (Andean margins lane). Needs a sourced shortening budget tied to convergence; judge on share of land >3 km near ocean-continent margins together with the overshoot judge and the hard bar; watch the volume thermostat (PW-1293) and arc CO2 (arc_nom).

## Updates
- 2026-11-10: Status in-progress -> done. Lane 275/275b, fourth attempt: post-orogenic collapse (crust not squeezed for 20 Myr flows 31x faster, volume kept) plus Andean shortening at share 0.1, both on by default (commit c219720a). In plain words: dead mountain belts now come down within 30-60 Myr instead of lasting hundreds of Myr, so more of the high ground sits on ocean-continent coasts. Coordinator ruling (geophysics delegation, option B of lane 275's draft): scout8.md's continental-crust line of 38% is read over the three seeds, since main itself is 37.8% on seed 1. Screen (L6 seeds 1/2/6001 x 600 Myr vs main a784b8ea same seeds): Andes share 21.5% mean (main 10.2%); land above 3 km 2.26% (main 2.76%); land within 1.4 points; continental crust median 37.9/38.5/38.9 (main 37.8/39.0/39.1). Fork screen (seeds 1/2/77/3199, fork 200 -> 400 Myr, 4 draws per arm, vs main a784b8ea's base+rng1-3 and fp-null): inland, lakes and giant-lake measures no consistent sign (stratified permutation p 0.53-0.91); discharge to the sea higher on all four seeds (+1-5%, p 0.07), noted, not a bar. Paired judge (18 L6 1 Gyr draws, roll 0.0005, vs main a626c541): hard failures 0/18 both; pass 17/18 both (McNemar p 1.0); late dT median shift -0.8 C (CI -1.3..+0.5); hot desert -2.2 points (p 0.03); glacial maxima 10 vs 3 of 18. Scorecard (seeds 1-2, 1 Gyr, vs main a626c541 run the same day): no hard failure; Earth identical; land >4 km at 1 Gyr 2.35/4.86% (main 1.35/1.86%), mean over the 100-Myr snapshots 1.9/1.4% (main 1.3/0.8%); dry 17.4/14.0% (main 24.7/24.4%). overview.md section 7 "Andean margin" rewritten with the sources.
- 2026-11-10: Status wontdo -> in-progress. Owner 11-10: prioritise Andes-type ranges. Reopened as a fourth attempt with his go-ahead (lane 275): diagnosis-led, testing whether belts survive too long once their trench dies (scout 237: 3/4 of high ground >240 km from a live margin) and adding post-orogenic decay to option A.
- 2026-11-09: Status in-progress -> wontdo. Strike 3 of 3 (scout 240, scout8.md): overriding-plate contraction at the long-term rate fails on L6 seeds 1/2/6001 x 600 Myr against main on the same seeds. Share 0.1: Andes share 15.9% mean (main 16.0%), land >3 km 5.26% mean (main 2.27%); share 0.05: 10.8% and 3.71%. No rate gives both margin ranges and main-like total high ground. Closed under PW-1509 option B (known Earth difference, overview.md section 7); mechanism removed from planet/, kept as docs/review/tectonics/mountains/scout7_andean.patch.
- 2026-11-08: Status todo -> in-progress. Scout 237 launched 11-08 night (Daniel asked): PW-1509 option A, overriding-plate contraction; strike 2 of 3.
- 2026-11-08: Scout 209 pass 1 (scout6.md): rate is not the problem; every stand-in for shortening on rigid plates breaks the volume or area thermostat. Strike 1 of 3. Next attempt only with real overriding-plate contraction (PW-1509 option A). Parked at later.
- 2026-11-07: Created.
