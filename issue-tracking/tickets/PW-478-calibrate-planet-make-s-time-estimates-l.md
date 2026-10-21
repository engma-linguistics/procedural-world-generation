---
id: PW-478
title: Calibrate planet make's time estimates (L4/L5/L8 and the time zoom, finish, highlights and zoom stages are scaled guesses)
type: task
status: done
parent: PW-244
milestone: v1
subsystem: infra
effort: xs
impact: low
found_by: agent-make-ui
blocked_by: []
relates: [PW-248, PW-472]
refs: [planet/make.py, docs/coordination.md]
created: 2026-10-20
updated: 2026-10-21
---

## Description
`make.estimate` (the form's "About 7 min" and the progress bar's stage weights) uses the run-cost table for L6/L7/L8 and the speed-pass numbers for time zooms (100 kyr = 10 s at L6, 31 s at L7). L4 and L5 run costs are scaled from the cell counts, and the finish, highlights and zoom stage times are rough (L6: 6, 10 and 5 s). The weights only shape the progress bar, but the total is shown to the owner. After a few real L6/L7 `planet make` runs on the owner's machine, put the measured stage times into `RUN_S_PER_GYR`, `TZ_S_PER_KYR`, `FINISH_S`, `HIGHLIGHTS_S`, `ZOOM_S` (and the run-cost table in docs/coordination.md). Machine load changes them by 2x or more, so the form says "about".

## Updates
- 2026-10-21: Status todo -> done. 2026-10-21: Fitted from the store's own timings; replaces the scaled guesses in planet/make.py. Sources: L6 runs 2 Gyr in the store (705 and 802 s/Gyr) and the health sweep of 2026-10-15 (8 L6 seeds, 1 Gyr, 11 workers at once, median 659 s); L7 health sweep (3 seeds, 1 Gyr, 2965-3038 s); time zooms in the store (300 kyr: 64 and 58 s; 600 kyr: 129 s); worlds' finish (6.6, 8.5, 6.9 s); highlights (1.15, 1.17 s); regional zooms (median 15 s for 500 px at 500-1000 km, 25-50 km about 5 s). Fit, new (old) values: RUN_S_PER_GYR L6 705 (330), L7 3010 (1800), L4 230 (25), L5 400 (80), L8 12000 (12600). TZ_S_PER_KYR L6 0.21 (0.1), L7 0.65 (0.31) via the speed-pass ratio, L4/L5/L8 scaled. FINISH_S L6 7 (6), L7 29 (20), L4 1, L5 2, L8 117 (80). HIGHLIGHTS_S L6 1.2 (10), L7 4.8 (40), L4 0.3, L5 0.5, L8 19 (150). ZOOM_S L6 15 (5), L7 21 (7), L4 8, L5 11, L8 30 (12). Measured only: L4 has one 100 Myr run (23 s into a scratch store; the first run may include start-up). L5 and L8 have no data (scaled). Load: store timings are on this machine at its usual load (2-63 load average in the sweep), so the form stays 'about'. test_make now asserts the L6 simulate estimate is 10-14 min. docs/coordination.md run-cost rows for L6 and L7 updated. Follow-up: issue-tracking/inbox/draft-make-estimate-unmeasured-levels.md.
- 2026-10-20: Created from inbox draft draft-make-estimate-calibration.md (found by agent-make-ui).
