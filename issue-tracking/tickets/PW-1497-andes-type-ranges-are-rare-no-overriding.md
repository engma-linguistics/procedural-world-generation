---
id: PW-1497
title: "Andes-type ranges are rare: no overriding-plate shortening at ocean-continent trenches (runs 8-10% of land >3 km near such margins, Earth 25%)"
type: task
status: wontdo
parent: null
milestone: later
subsystem: tectonics
effort: l
impact: med
found_by: scout1-mountains
blocked_by: []
relates: []
refs: [docs/review/tectonics/mountains/scout1.md]
created: 2026-11-07
updated: 2026-11-09
---

## Description
In plain words: on Earth a quarter of the land above 3 km is the central Andes, on an ocean-continent margin. In our runs only 8-10% of high ground is near such a margin, because the model only thickens crust at a trench by arc magmatism; it never shortens the overriding plate, so continent-continent collision is the only way to stack crust. See docs/review/tectonics/mountains/scout1.md (Andean margins lane). Needs a sourced shortening budget tied to convergence; judge on share of land >3 km near ocean-continent margins together with the overshoot judge and the hard bar; watch the volume thermostat (PW-1293) and arc CO2 (arc_nom).

## Updates
- 2026-11-09: Status in-progress -> wontdo. Strike 3 of 3 (scout 240, scout8.md): overriding-plate contraction at the long-term rate fails on L6 seeds 1/2/6001 x 600 Myr against main on the same seeds. Share 0.1: Andes share 15.9% mean (main 16.0%), land >3 km 5.26% mean (main 2.27%); share 0.05: 10.8% and 3.71%. No rate gives both margin ranges and main-like total high ground. Closed under PW-1509 option B (known Earth difference, overview.md section 7); mechanism removed from planet/, kept as docs/review/tectonics/mountains/scout7_andean.patch.
- 2026-11-08: Status todo -> in-progress. Scout 237 launched 11-08 night (Daniel asked): PW-1509 option A, overriding-plate contraction; strike 2 of 3.
- 2026-11-08: Scout 209 pass 1 (scout6.md): rate is not the problem; every stand-in for shortening on rigid plates breaks the volume or area thermostat. Strike 1 of 3. Next attempt only with real overriding-plate contraction (PW-1509 option A). Parked at later.
- 2026-11-07: Created.
