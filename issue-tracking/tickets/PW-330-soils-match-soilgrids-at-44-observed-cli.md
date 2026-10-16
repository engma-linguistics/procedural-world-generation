---
id: PW-330
title: Soils match SoilGrids at 44% (observed climate), short of the 50% target
type: task
status: todo
parent: PW-184
subsystem: surface
effort: m
impact: med
found_by: soils
blocked_by: []
relates: [PW-185, PW-037, PW-132]
refs: [planet/soils.py, tools/soil_check.py, docs/review/soils/earth_groups.png, "docs/overview.md#2.21"]
created: 2026-10-16
updated: 2026-10-16
---

## Description
`tools/soil_check.py` (L6 Earth world, GLiM rock, LGM ice): 10-group area-weighted agreement with SoilGrids WRB is 44.1% on the observed climate (33% on the model's), below the proposal's "good enough" 50%. Tuning stopped at sound choices; what is left:
- SoilGrids' Cambisols and Regosols (22% of land) are spread by the model over thin (3.6 Mkm2), frozen (3.3, mountain permafrost), desert (4.4, dry Cambisols called caliche) and brown forest soils (3.1). The young group is 13% in the model vs 22%.
- Desert group 20.6% vs 14.6%: dry-margin Luvisols, Regosols and Kastanozems come out as caliche.
- Earth has no dune-field or young-volcano landforms (PW-132): Arenosols only from deflated sediment, Andosols only on GLiM pyroclastics (5% of Japan-Java-Andes).
- Vertisols in Sudan: GLiM calls the Gezira unconsolidated sediment, not a clay-rich parent.
- Loess on the Loess Plateau is 2-4 m (Earth ~100 m): the model's winds and the desert source strength; PW-037 will replace the glacial half.
- Generated worlds: the run's cover rock is ~45% sandstone (world 592f2a's strata_top), so sand and podzol rules key on it a lot; tropical red soils cover 30-40% of land on three L7 worlds (warm worlds, or W runs high).
Ideas: a soil-age term for colluvial/young hillslopes (Cambisols), a lime-accumulation index rather than a dryness cut, a coarse parent-material class set (PW-185 GLiM note, option B) if the rock mapping limits it.
- [ ] observed-climate agreement >= 50% with sound rules, or a documented reason why not

## Updates
- 2026-10-16: Created from inbox draft draft-soil-earth-agreement.md (found by soils).
