---
id: PW-134
title: Per-cell records (and rock, cover) flicker frame to frame as the world grid resamples the plates
type: task
status: todo
parent: null
subsystem: tectonics
effort: m
impact: med
found_by: landform
blocked_by: []
relates: [PW-108, PW-009]
refs: [planet/landform.py, planet/tectonics/simulation.py, "run 472faf (deleted; rerun seed 21 L7)"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Each world cell shows the record of the one plate cell nearest to it. As a
plate rotates, a world cell maps to a different plate cell now and then, and
neighbouring plate cells differ a lot in detail: on the L7 seed-21 run at
404 -> 408 -> 412 Myr, sediment cover changes by a median 12% per land cell
in 4 Myr, the basement `rock` layer changes on 15.7% of land cells (2.8%
flip back at the next frame), `surface_rock` on 27% (4.4% flip back), and
the raw landform classes on 28% (7.3% flip back). Examples: a cell whose
strata read [shale 2.14 km] -> [sandstone 0.4 / shale 2.0] -> [sandstone
0.13 / sandstone 0.05 / shale 3.5] on the same plate in three frames.
The landform classifier now runs one majority-filter pass over the areal
classes (`landform.smooth`), which brings it to 21% change / 4.1% flip-back,
on a par with `surface_rock`.

The cause is cell-scale heterogeneity in the plate frame (per-cell erosion
and deposition differences that never diffuse within a plate) plus the
nearest-neighbour sampling, and at converging boundaries PW-108's churn.
Options: a little lateral diffusion of cover thickness within a plate; or
gather the world view with a smoother sampling for display layers. Look at
it together with PW-108.

## Updates
- 2026-10-14: Created from inbox draft draft-record-speckle-flicker.md (found by landform).
