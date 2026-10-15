---
id: PW-130
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
created: 2026-10-14
updated: 2026-10-14
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

## Updates
- 2026-10-14: zoomland3 (PW-012): the zoom's karst synthesiser now exists; on a08983 all 204 karst cells are still low coastal platforms (median 14 m), so real zooms show lowland karst (towers on a plain, dolines, flooded poljes); the Dinaric upland look is only seen in synthetic tests (docs/review/landforms/zoom_karst_synthetic_temperate_tropical.png).
- 2026-10-14: Created from inbox draft draft-carbonate-rare-on-land.md (found by landform).
