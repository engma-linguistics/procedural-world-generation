---
id: PW-040
title: Speckled temperatures over the Andes and the Tibetan margin
type: task
status: done
parent: null
subsystem: climate
effort: s
impact: low
found_by: viewer2
blocked_by: []
relates: []
refs: [planet/climate.py, "world 2f38e3"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
The Earth world's temperature-difference view is speckled cell to cell over the Andes and the Tibetan
margin (likely elevation sampling or lapse rate on steep cells). Check on 2f38e3.

## Updates
- 2026-10-14: Status todo -> done. Fixed in ffecac0 (climfix): the speckle was in the observations, not the model. The model is smooth once its lapse rate is taken out (0.2 C cell-to-cell); NCEP was sampled nearest-pixel at its ~1.9 deg terrain. Observed temps are now sea-level reduced, bilinear, and taken to each cell's height: model-minus-observed roughness over the Andes/Tibet margin 2.0-2.75 -> 0.5-0.7 C. World 2f38e3 needs remaking (inbox draft).
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Climate (seen on 8e052d, now deleted).
