---
id: PW-608
title: "Resources: what the run could record so resources need fewer proxies (for the run-physics lane)"
type: task
status: todo
parent: PW-155
milestone: later
subsystem: tectonics
effort: m
impact: low
found_by: resources
blocked_by: []
relates: [PW-155, PW-212, PW-134, PW-474]
refs: [planet/resources.py, planet/tectonics/record.py]
created: 2026-10-23
updated: 2026-11-03
---

## Description
planet/resources.py reconstructs each cell's past from the keyframes (tracing ground back along
plate rotations; rebuilding a 10-layer column from cover changes). It works (1.5 s L6) but has proxies the
run could replace cheaply, as record fields riding with the crust (no new time-stepped physics):
1. **Arc time** (Myr the crust sat in an arc) and **max crust thickness** (with when): now accumulated from
   traced keyframes (landform 11, crust_thickness), which smears across cells where tracing drifts.
2. **Coal from buried peat** (PW-212): the column's coal-bearing layers come from keyframe swamp conditions
   (warm, wet, low, forested); the run's own coal stratum uses `veg > 0.5`. A coal fraction per stratum would
   make the two agree.
3. **Organic-rich source rock**: no flag; proxy = shale on continental crust under seas < 1200 m. An
   anoxia/productivity flag at deposition (restricted basin, upwelling) would help oil.
4. **Ophiolite / suture tag**: laterite nickel needs ultramafic rock; there is none, so laterite_ni covers
   ~0.1% of land on every world. Obducted ocean crust at collisions (a flag on the cells a collision closes
   over) would fix it.
5. The column inherits the keyframes' 0.1 km cover quantisation and the frame-to-frame flicker (PW-134):
   coal maps come out speckled.
Meanwhile the proxies stay; none of this blocks stage 1 or 2.

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: resources/ore layer or salt-mining detail; not needed for the first culinary brief
- 2026-10-23: Created from inbox draft draft-resources-run-record.md (found by resources).
