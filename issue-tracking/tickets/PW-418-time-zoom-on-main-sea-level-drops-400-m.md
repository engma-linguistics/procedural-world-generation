---
id: PW-418
title: "Time zoom on main: sea level drops ~400 m in 50 kyr, and carving erodes 10-50x too much"
type: task
status: done
parent: PW-037
subsystem: timezoom
effort: m
impact: high
found_by: pw037
blocked_by: [PW-366]
relates: [PW-037, PW-031, PW-367]
refs: [planet/timezoom.py, planet/timezoom_kernels.py, docs/review/audit/pw037-handoff.md]
created: 2026-10-16
updated: 2026-10-21
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
- 2026-10-21: Status blocked -> done. Resolved by PW-471 (bounded ice on Earth) and pw037-port: the sliding speed is taken at a basal stress of at most the bed's yield stress (the physical form of option a), so margin cliffs and drifting sheets no longer erode 10-50x too much; Earth L6 600 kyr now 43 m/Myr mean, p99 300 under the ice. The run-moment drift itself is PW-492's. docs/review/audit/PW-037-handoff.md.
- 2026-10-16: Status todo -> blocked. Bisected (pw418): no time-zoom commit since 1f0fae4 causes it; the jump is 1416523 (PW-015 stage 1 rain) alone. 20 kyr default from 2c2810 @ 536: 1f0fae4 -108, 415c60b -92, 1416523 -199 (= main); from the L6 seed-2 run @ 580 (rebuilt as e438c3, identical to 6d67bd: main gives -487 m at 50 kyr): -91 / -115 / -314 (= main). The new rain snows ~35% more on the generated sheets (Earth's only +5-9%), so the run's ice rule makes ~2x the sheets at the same climate and the time zoom's old start surplus (PW-366: thin run sheets can't feed their ablation zone; PW-241, PW-295) grows. Ice speeds aren't the cause: grounded (>100 m) medians 9-26 m/yr before and after, p99 0.5-2 km/yr (2c2810: 9 -> 18 m/yr median, more and thicker ice); the ~1 km/yr median wasn't reproduced. Not fixed here: the cause is in the run's ice rule / shared rain (simulate outputs, other lane): draft draft-rain-stage1-snowier-sheets-time-zoom-drift.md (needs-decision; lean: fix PW-366 first). Found and not merged: thin films beyond a front hide it from the margin rule (draft draft-timezoom-film-shielded-margins.md; the simple fixes trade the advance for a melt cascade). Added tests/test_timezoom_consistency.py (slow, L5): the run's ice rule's sheets then 20 kyr unforced: speeds plausible (pass), sea level within 25 m (xfail strict on PW-366, -58 m now). For PW-037 (pw037-carving, parked): don't recalibrate on main's current ice; once PW-366 (and the rain decision) land, re-fit glacial_k on the corrected run (1 Myr: tens of m mean, ~100-200 m p90 under the ice) and take the sliding speed only on grounded ice thicker than edge_h (handoff option a), since the extreme D|grad s|/H values sit on cliff-like margin cells and grow with sheet size; re-run the 100 kyr erosion check from 2c2810 @ 536 and e438c3/6d67bd @ 580.
- 2026-10-16: Created from inbox draft draft-timezoom-fast-drift-and-carving-recalibration.md (found by pw037).
