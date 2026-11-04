---
id: PW-630
title: "Zoom soils: a salt pan's cell makes every pixel of it salty"
type: task
status: todo
parent: PW-184
milestone: later
subsystem: zoom
effort: s
impact: low
found_by: soilveg2
blocked_by: []
relates: [PW-330, PW-649]
refs: [planet/zoom/vegetation.py, planet/soils.py]
created: 2026-10-23
updated: 2026-11-03
---

## Description
`zoom_vegetation` passes the coarse cell's `soils.salt_near` to every pixel. Since PW-330 that is only the cell holding the closed lake or salt pan (no longer its neighbours too), but within that cell all pixels, slopes included, become salt-crusted soil. Salt soils belong on the pan floor and its fringe: pixels that are flat and within a few metres of the pan's level.
- [ ] zoom salt soils only on the flat low ground around the pan

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: zoom polish; zooms are good enough to read
- 2026-10-23: Filed under the quality-pass epic PW-649 (relates PW-649): shipped and judged good enough, residual kept for a later cleanup pass.
- 2026-10-23: Created from inbox draft draft-soil-zoom-salt-pixels.md (found by soilveg2).
- 2026-10-30: planet/zoom.py and planet/zoom_*.py moved into planet/zoom/ (regional.py, fine.py, ...) and zoom.build split into named stages (stage_*.py), lane 55; the file names here are the new ones, but the line numbers in the text are from before the move.
