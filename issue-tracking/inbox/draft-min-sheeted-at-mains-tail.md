---
title: "MIN_SHEETED = 5 sits at main's own low tail: re-rolled draws give 7, 10 and 5 sheeted cold moments, so one more unlucky draw turns test_cold_moment_has_sheets red on main"
type: task
status: needs-decision
parent: PW-470
milestone: v1
subsystem: timezoom
effort: xs
impact: med
found_by: tests-multiseed-rulings
blocked_by: []
relates: [PW-643, PW-623]
refs: [tests/test_timezoom_consistency.py, docs/review/tests/multiseed-fixtures.md]
---

## Description
The owner kept `MIN_SHEETED = 5` (PW-643). On main 9b30887 the L5 window (seeds 25-50) gives these sheeted plausible
cold moments in three null draws (`PW_SEED_OFFSET`, climate_offset 0 / +0.001 / -0.001 C):

| draw | sheeted of plausible |
|---|---|
| 0 | 7 of 14 |
| +0.001 | 10 of 13 |
| -0.001 | 5 of 10 |

The -0.001 draw sits exactly on the bar. A20 gives 4 of 8. This is the same lottery PW-643 removed from the L4
tests, now on a count.

Options:
- A: keep 5.
- B: widen the window (seeds 25-75, about +1 min of suite time). Main would then give roughly 10-20.
- C: 4.
- Lean: B. It keeps "enough worlds for the drift tests" without lowering the bar.
- [ ] A / B / C
