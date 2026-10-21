---
id: PW-478
title: Calibrate planet make's time estimates (L4/L5/L8 and the time zoom, finish, highlights and zoom stages are scaled guesses)
type: task
status: todo
parent: PW-244
subsystem: infra
effort: xs
impact: low
found_by: agent-make-ui
blocked_by: []
relates: [PW-248, PW-472]
refs: [planet/make.py, docs/coordination.md]
created: 2026-10-20
updated: 2026-10-20
---

## Description
`make.estimate` (the form's "About 7 min" and the progress bar's stage weights) uses the run-cost table for L6/L7/L8 and the speed-pass numbers for time zooms (100 kyr = 10 s at L6, 31 s at L7). L4 and L5 run costs are scaled from the cell counts, and the finish, highlights and zoom stage times are rough (L6: 6, 10 and 5 s). The weights only shape the progress bar, but the total is shown to the owner. After a few real L6/L7 `planet make` runs on the owner's machine, put the measured stage times into `RUN_S_PER_GYR`, `TZ_S_PER_KYR`, `FINISH_S`, `HIGHLIGHTS_S`, `ZOOM_S` (and the run-cost table in docs/coordination.md). Machine load changes them by 2x or more, so the form says "about".

## Updates
- 2026-10-20: Created from inbox draft draft-make-estimate-calibration.md (found by agent-make-ui).
