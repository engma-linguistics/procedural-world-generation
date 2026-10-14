---
id: PW-006
title: "Per-cell stratigraphy: ordered record of the top few layers"
type: story
status: done
parent: PW-005
subsystem: surface
effort: l
impact: high
found_by: daniel
blocked_by: []
relates: []
refs: [planet/surface.py, planet/tectonics/crust.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Cells keep one rock id plus sediment cover today. Keep an ordered stack of the top few layers
(rock type, thickness, age, flat vs folded), on the plate frame so it moves with the crust. What
matters for landforms is hard-over-soft (caprock over shale makes scarps and falls) more than the
number of rock types. Keep memory and checkpoint size in mind (L7 checkpoints are already large).

## Updates
- 2026-10-14: Status todo -> done. Strata in tectonics/record.py: top 3 layers per plate cell (km, rock, last grew), riding with the crust (Plates.rec/lith), always summing to the cover; L7 cost ~3-4% of a step, +~0.45 GB plate arrays, checkpoints ~80-130 MB (record of unowned cells zeroed). Branch landform.
- 2026-10-14: Created from the landform-classes epic (owner discussion 2026-10-14).
