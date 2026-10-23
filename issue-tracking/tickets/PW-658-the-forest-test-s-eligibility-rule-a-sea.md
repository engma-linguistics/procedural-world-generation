---
id: PW-658
title: "The forest test's eligibility rule (a season of snow under the boreal forest) separates only moderately: 80% of eligible worlds pass, 41% of ineligible ones"
type: task
status: todo
parent: PW-649
milestone: null
subsystem: timezoom
effort: s
impact: low
found_by: tests-multiseed-rulings
blocked_by: []
relates: [PW-645, PW-643, PW-450]
refs: [tests/test_timezoom.py, docs/review/tests/multiseed-fixtures.md, docs/review/tests/eligibility.txt]
created: 2026-10-23
updated: 2026-10-23
---

## Description
The rule adopted for PW-645 is `_boreal_snow >= 3/12`: the start's forest poleward of 40 deg lies under snow at least
a season of the year, on the tree-weighted mean. The only number in it is "a season". Measured on main's 120 L4
worlds (seeds 1-24 in three draws, plus seeds 25-72):
- 78 of 98 eligible worlds pass;
- 9 of 22 ineligible worlds pass.

At the 50% bar that is lottery-proof. But the premise still fails on about 1 in 5 eligible worlds.

Rules that separate better, from `docs/review/tests/eligibility.txt`:
- A21's snow cover on open land >= 0.12: 56 of 60 eligible pass. It needs an Earth-ish number.
- run dT <= +5: 73 of 85. Not planet-relative.

A physically sharper rule would compare the two parts of the premise, both read at the start:
- the snow brightening the boreal forest hides (W/m2: sun x snow cover x the forest's mask x (snow albedo - its
  albedo));
- the darkening that greening the low-latitude bare ground could give.

It would have no arbitrary number, but it needs care so that it doesn't amount to computing F.

## Updates
- 2026-10-23: Created from inbox draft draft-forest-eligibility-sharper-rule.md (found by tests-multiseed-rulings).
