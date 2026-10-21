---
title: Flat basin floors and landform-lake shores still dead flat after the shore apron (PW-531)
type: task
status: todo
parent: null
subsystem: zoom
effort: m
impact: low
found_by: pw531
blocked_by: []
relates: [PW-531, PW-521]
refs: [planet/zoom.py, "zoom f24fda (Costa Rica, 18 iterations)", "zoom 9213a8", "zoom 4f65aa"]
---

## Description
PW-531's shore apron (`shore_apron`, coarse lakes of at least 150 km2) took the Costa Rica zoom's land above 300 m
with slope under 1 m/km from 8002 km2 to 1554 km2. What is left there, and elsewhere:
- A ~800 km2 pale flat basin in the SW of the Costa Rica zoom (near the SW corner, about 130 km from the west and 60 km from the south edge; the
  lighter patch in docs/review/screens/pw531-costa-rica-before-after.png). It is not a lake rim; probably a salt
  pan / playa or a landform basin floor that grade_fills (PW-521) did not take.
- Shores of landform-basin lakes (zoom_landforms basin_lakes, `lf_lake`), which are not in `lakes` and so get no
  apron: Labrador zoom 4f65aa has 432 km2 of such flat land within 40 km of a lake, Baltic 9213a8 96 km2.
- A beach strip 1-3 px wide along the big lake's shore (intended), and river valley floors above SHORE_RIVER_Q.
- [ ] decide whether landform lakes should get the same grade (the apron works from `lakes`' pixel lists and
  `ZK.raise_to_run`), and whether the SW basin is a pan that may stay flat (a salt pan is legitimately flat)
