---
id: PW-210
title: "Vegetation on the model's Earth climate: 44% potential-vegetation agreement (target 50%), from climate errors"
type: task
status: todo
parent: null
subsystem: climate
effort: m
impact: med
found_by: veg
blocked_by: []
relates: [PW-013, PW-015, PW-038, PW-187]
refs: [tools/veg_check.py, "world fe2af4"]
created: 2026-10-15
updated: 2026-10-15
---

## Description
tools/veg_check.py runs the vegetation on Earth's terrain twice. On the observed climate it agrees with potential natural vegetation on 62% of the land (target 60%); on the model's climate only 44% (target 50%). The gap is the climate's: the model's Amazon gets ~750 mm/yr with a 5-month dry season (observed 2000-2400 mm), so it is savanna; the Sahel at 0E is far too wet; NE Canada is too warm, so the treeline is 8-12 deg too far north there (sectors -90 and -60). Biggest confusion: potential forest -> model savanna (~17 Mkm2) and forest -> grassland (~9). Nothing to fix in the vegetation; use veg_check's model-climate numbers as a further score for the rain work (PW-013/PW-015) and PW-038.

## Updates
- 2026-10-15: Created from inbox draft draft-veg-model-climate-agreement.md (found by veg).
