---
id: PW-1266
title: "Refined worlds: rain is the L7 climate's, spread smoothly; no rain shadow or windward rain below 55 km"
type: task
status: todo
parent: PW-1198
milestone: later
subsystem: climate
effort: m
impact: med
found_by: lane104-refine-l8
blocked_by: []
relates: [PW-101, PW-290, PW-490]
refs: [planet/nest.py, planet/refine.py, docs/review/refine-l8/design.md]
created: 2026-11-01
updated: 2026-11-03
---

## Description
**In plain words.** A refined L8 world gets its temperatures right cell by cell (each fine cell's own height through
the lapse rate). Its rain, though, is the L7 climate's, spread smoothly over the finer cells. A ridge that only exists
at L8 gets no wetter windward side and no drier lee.

`planet refine` runs the climate on the L7 grid and brings it down with `nest.climate_coarse` (the run's L7-on-L6
machinery). Rain shadows exist at the 55 km scale. Below that, rain varies linearly between L7 cells.

Try: a per-fine-cell orographic factor from the wind (the July and January winds, already on the fine cells) and the
fine slope against the parent's mean slope. Rescale it so each L7 cell keeps its rain total (the terrain's
mean-keeping rule). PW-101 asks for the same in the regional zoom, so one function could serve both.
- [ ] refined L8: windward/lee rain ratio on fine ridges in a plausible range; each L7 cell's rain total kept

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: rain kernel is calibration polish and three strikes sends it to the back of the line (PW-1363)
- 2026-11-01: Created from inbox draft draft-refine-sub-cell-orographic-rain.md (found by lane104-refine-l8).
