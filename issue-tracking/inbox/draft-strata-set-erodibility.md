---
title: Let the exposed stratum, not the well-mixed cover, set surface rock and erodibility
type: task
status: needs-decision
parent: PW-005
subsystem: surface
effort: m
impact: med
found_by: landform
blocked_by: []
relates: [PW-006, PW-010]
refs: [planet/tectonics/record.py, planet/surface.py, planet/landform.py]
---

## Description
The landform branch added an ordered record of each cell's top 3 strata
(`tectonics/record.py`), but the cover that erosion and isostasy use is still
one well-mixed column (`isostasy.EXTRA` MIX). So two notions of "what is
exposed" now coexist: `surface_rock` (the mix's main ingredient) and
`strata_top` (the real top layer, e.g. 0.2 km of dolomite over shale). Erosion
uses the mix's mean erodibility, so a hard caprock doesn't protect the soft
rock under it in the run; only the zoom will draw the scarp.

Options:
- **A.** Keep it as is: the record is diagnostic; caprock steps only appear
  in the zoom (PW-010). No model change.
- **B.** Make `surface_rock` = `strata_top` (display and zoom lip resistance
  only). Small; highlights' evaporite/limestone detectors then read the
  ordered top (dolomite must count as carbonate there).
- **C.** B plus erosion K from the exposed stratum (with the mix as the
  fallback where the strata are thinner than a step's erosion): caprock
  protects, soft beds strip fast, plateaus and cuestas emerge in the run
  itself. Physics depth, but it moves erosion everywhere: rerun the
  scorecard and expect retuning.

Lean: B now, C as an experiment after PW-010 shows what the zoom needs.
