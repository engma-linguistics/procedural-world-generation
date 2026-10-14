---
id: PW-136
title: Let the exposed stratum, not the well-mixed cover, set surface rock and erodibility
type: task
status: todo
parent: PW-005
subsystem: surface
effort: m
impact: med
found_by: landform
blocked_by: []
relates: [PW-006, PW-010]
refs: [planet/tectonics/record.py, planet/surface.py, planet/landform.py]
created: 2026-10-14
updated: 2026-10-14
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

## Updates
- 2026-10-14: Option B done (branch stratarock): surface_rock in snapshots/keyframes and worlds (world_from_frame recomputes it from the stored strata) is the exposed stratum (record.top through landform.VENEER_KM), the basement under < 50 m (COVER_SHOWS) of cover, shale for a cover of veneers only. Run evolution bit-identical (L6 seed 21, 300 Myr, 30 keyframes: only surface differs; golden only snap_surface). On f59dd6 @ 408 Myr land: sandstone 43.5->34.2%, shale 12.4->28.1%, coal 7.9->0.3%, limestone 0.8->1.4%, quartzite 0->0.3%; karst shows carbonate 18->100%, caprock hard-over-soft cells show the hard top 78->100%. Highlights count dolomite as carbonate. C (erosion K from the exposed stratum) remains, after PW-010.
- 2026-10-14: Status needs-decision -> todo. Owner decision (2026-10-14): B now (the exposed stratum sets surface_rock and the zoom's rock/erodibility, display only), C (feed erosion so caprock protects in the run) after the first zoom batch PW-010.
- 2026-10-14: Created from inbox draft draft-strata-set-erodibility.md (found by landform).
