---
id: PW-009
title: Assign a landform class to each cell from its history
type: story
status: done
parent: PW-005
subsystem: surface
effort: m
impact: high
found_by: daniel
blocked_by: [PW-006, PW-008]
relates: []
refs: [planet/world.py, "world 2f38e3"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
From stratigraphy, history and current setting (relief, climate, coast), assign one of 8–12 classes per
cell (see the epic's list), stored as a world layer and shown in the viewer. Start with the 3–4 classes
of the first zoom batch and add more as each batch lands. Check the class map on the Earth world
(2f38e3) where possible, and on a showcase.

## Updates
- 2026-10-14: Status todo -> done. landform.py: 12 classes (hills, shield, fold belt, rift, escarpment, caprock, lava plateau, karst, dunes, coastal plain, arc, hotspot) + zoom params (landform_age, strata_top/_km/_next, strata_dip, fold_wavelength) in keyframes, worlds, legend 'landforms', zoom per-pixel landform, viewer layer. L7 run f59dd6, world 800c99; docs/review/landforms/. Earth world: no record (draft).
- 2026-10-14: Created from the landform-classes epic (owner discussion 2026-10-14).
