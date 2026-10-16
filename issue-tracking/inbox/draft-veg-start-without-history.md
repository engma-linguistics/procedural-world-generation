---
title: "Vegetation: what a world without history (Earth, generate) starts from decides forest vs savanna on the Amazon fringe"
type: task
status: needs-decision
parent: null
subsystem: surface
effort: s
impact: low
found_by: vegbatch
blocked_by: []
relates: [PW-205, PW-187]
refs: [planet/vegetation.py, tools/veg_check.py]
---

## Description
The last open item of PW-205: on Earth (observed climate) 57 of the 135 southern-Amazon-fringe cells (18-7 S, 65-45 W) that potential vegetation calls forest are savanna, and 31 of 46 on the Brazilian shield. Forest and savanna are both stable there (fire with a 3-4 month dry season), so the start decides. A world with history (sliced from a run, the Zoom button) starts from the run's state; Earth and `generate` worlds start from `vegetation.START` (trees 0.4, herbs 0.3: young woodland over grass). Measured with tools/veg_check.py logic on the observed climate (batch 2026-10-16 code):

| start (trees, herbs) | agreement | forest Mkm2 | savanna + trop. grass | burned Mkm2/yr | Amazon fringe forest / savanna | Med. cells | NPP |
|---|---|---|---|---|---|---|---|
| 0.4, 0.3 (now) | 59.5% | 46.2 | 18.6 | 4.3 | 77 / 57 | 124 | 57.0 |
| 0.8, 0.1 (closed forest) | 59.0% | 55.6 | 10.5 | 2.3 | 123 / 11 | 89 | 51.9 |
| 0.1, 0.6 (grassland) | 59.4% | 45.7 | 19.1 | 4.4 | 69 / 65 | 124 | 57.3 |

Options:
- (A) Keep young woodland over grass (now): savanna area and burned area near Earth's, the Amazon fringe and Brazilian shield too open.
- (B) Start from closed forest: the fringe is forest, but savanna halves (10.5 Mkm2 vs ~20), fire halves, Mediterranean scrub shrinks; a forest start everywhere is the opposite bias (Earth's savannas have a long fire history).
- (C) A start from the climate: closed forest where the wet season is long (e.g. fewer than ~3 fire-weather months), open woodland elsewhere: a rule chosen to put the boundary somewhere, so it is close to forcing.
Lean: A (history decides, and Earth has none; potential vegetation's "forest" on the Brazilian shield is partly cerrado anyway).
