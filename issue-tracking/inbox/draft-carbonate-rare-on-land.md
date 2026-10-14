---
title: Carbonate strata rarely reach the land surface (karst 0.4% of land; Earth ~10%)
type: task
status: todo
parent: PW-005
subsystem: surface
effort: m
impact: med
found_by: landform
blocked_by: []
relates: [PW-012]
refs: [planet/tectonics/earth.py, planet/landform.py]
---

## Description
On the L7 seed-21 run (408 Myr) limestone or dolomite is the exposed stratum
on under 1% of land, and karst (>= 0.4 km of carbonate, wet) covers 0.4%,
almost all of it on low coastal reef platforms (median elevation 31 m).
On Earth carbonate rocks crop out on ~10-15% of ice-free land, mostly from
epeiric (shallow continental) seas of past sea-level highstands. In the model
reefs only grow on warm shelves (`earth.reefs`, < -5 m and > -1500 m, >=
reef_temp) and the continents are seldom flooded, so platform carbonates are
thin and get buried under shelf mud. Worth checking: how much continental
area is shallow sea over a run, and whether carbonate production should
also include non-reef shelf carbonate (micrite, chalk) at lower rates in
warm and temperate shallow seas. Karst synthesis (PW-012) will have little
to draw until this changes.
