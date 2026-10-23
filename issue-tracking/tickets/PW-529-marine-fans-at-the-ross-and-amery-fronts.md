---
id: PW-529
title: Marine fans at the Ross and Amery fronts still reach 300-410 m
type: task
status: todo
parent: PW-649
milestone: v2
subsystem: timezoom
effort: xs
impact: low
found_by: pw497
blocked_by: []
relates: [PW-495]
refs: [planet/timezoom/deposit.py, planet/timezoom/params.py]
created: 2026-10-21
updated: 2026-10-23
---

## Description
After the fan spreading (PW-495: fan_km_r 0.08 radius = 510 km, fan_flat 1000 m), Earth L6 at 600 kyr has
no sea cell above 411 m (was 540-640 m), and no cell holds more than ~2.4x the mean of its neighbours.
4 cells are above 300 m (Ross 80.2 S 167 E and 81.2 S 169 E, Amery 69.7 S 70 E). The ticket's
rough 300 m is met by the other cells; going further would need a longer length than "a few cells"
(a longer fan_km_r) or a slope-limited relaxation of the till on the floor. Real trough-mouth fans are 1-4 km thick
over ~2.6 Myr, so 400 m in 0.6 Myr is not out of range.
- [ ] decide whether 411 m is acceptable; if not, a critical-slope relaxation of the sea-floor till

## Updates
- 2026-10-23: Filed under the quality-pass epic PW-649 (parent PW-649): shipped and judged good enough, residual kept for a later cleanup pass.
- 2026-10-21: Created from inbox draft draft-marine-fan-still-300m-at-ross.md (found by pw497).
