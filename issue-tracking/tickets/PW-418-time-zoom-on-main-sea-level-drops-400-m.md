---
id: PW-418
title: "Time zoom on main: sea level drops ~400 m in 50 kyr, and carving erodes 10-50x too much"
type: task
status: todo
parent: PW-037
subsystem: timezoom
effort: m
impact: high
found_by: pw037
blocked_by: []
relates: [PW-037, PW-031, PW-367]
refs: [planet/timezoom.py, planet/timezoom_kernels.py, docs/review/audit/pw037-handoff.md]
created: 2026-10-16
updated: 2026-10-16
---

## Description
After merging main into the PW-037 branch, the time zoom (carving off, i.e. main's own behaviour)
drifts much further than before:
- L6 seed 2, a fresh run on main (`planet simulate --seed 2 --level 6 --myr 600`), @ 580 Myr: sea level
  −117 m at 5 kyr, −487 m at 50 kyr, −304 m at 100 kyr.
- Old L7 run 2c2810 @ 536: −199 m at 20 kyr (main's code alone, run separately).
SIA speeds (D|grad s|/H) are ~1 km/yr at the median by 20 kyr, with 10-400 km/yr in a few cells. On the
old base they were 4-11 m/yr at the median. PW-037's carving, calibrated on the old speeds, now erodes
hundreds of metres in 100 kyr (mean 340 m under the ice at L6).
- [ ] decide whether the drift is a regression (ice shelves / buttressing, PW-367? polar changes?) and fix
  it if it is
- [ ] then recalibrate or robustify PW-037's sliding speed (handoff doc, step 2) before merging the
  pw037 branch

## Updates
- 2026-10-16: Created from inbox draft draft-timezoom-fast-drift-and-carving-recalibration.md (found by pw037).
