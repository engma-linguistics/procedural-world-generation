---
id: PW-629
title: "Soils: Ferralsols vs Acrisols can't be told apart at L6; profile age (PW-329) moves the split to 15% Ferralsols (SoilGrids 10.5%)"
type: task
status: done
parent: PW-184
milestone: v2
subsystem: surface
effort: s
impact: low
found_by: soilveg2
blocked_by: []
relates: [PW-329, PW-330]
refs: [planet/soils.py, tools/soil_check.py]
created: 2026-10-23
updated: 2026-10-23
---

## Description
PW-329 made W count the soil material's age since it left the weathering front ((saprolite + soil) / E, `soils.R_SAP`, `D_SAP`), so old flat wet surfaces carry tens of metres of saprolite and W rises by ~1 there. The tropical-red group is unchanged (22.2% of land vs SoilGrids 20.5%), but inside it Ferralsols grow from 9.9% to 15.2% of land (SoilGrids' Ferralsols + Nitisols + Plinthosols 10.5%) and Acrisols shrink from 12.3% to 7.0% (SoilGrids 9.9%). Placement improves (Ferralsols Amazon 64 -> 71%, Congo 48 -> 63%).
On Earth's observed climate the model's inputs don't separate SoilGrids' Ferralsol and Acrisol cells at all (median W 6.28 vs 6.35, saprolite 11 vs 12 m, slope 1.5 vs 1.5 m/km, erosion 0.005 mm/yr both), so neither a W_FERRALSOL change nor a saprolite-depth criterion would be a mechanism; it would only set the split. Left as is.
Decision: keep `W_FERRALSOL` 5.5 (more Ferralsols than Earth, but on the right ground), or raise it (~6.0) so the share stays near Earth's.

## Updates
- 2026-10-23: Status needs-decision -> done. Coordinator (owner delegates geophysics): keep the 5.5 threshold. The model has no signal separating SoilGrids' Ferralsol and Acrisol cells, so moving it would be fitting to Earth.
- 2026-10-23: Created from inbox draft draft-soil-ferralsol-acrisol-split.md (found by soilveg2).
