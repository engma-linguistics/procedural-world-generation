---
id: PW-659
title: "The forest-to-tundra test has no floor on how many worlds are eligible: a change that removes most boreal snow would leave it passing on a handful of seeds"
type: task
status: todo
parent: PW-649
milestone: v1
subsystem: timezoom
effort: xs
impact: low
found_by: tests-multiseed-rulings
blocked_by: []
relates: [PW-645, PW-643]
refs: [tests/test_timezoom.py, tests/seeds.py, docs/review/tests/multiseed-fixtures.md]
created: 2026-10-23
updated: 2026-10-23
---

## Description
PW-645's ruling made the forest test's seeds eligible by a rule on the world (`_boreal_snow >= SEASON`: the start's
forest poleward of 40 deg lies under snow at least 3 of 12 months). `seeds.check_rate` needs only `n > 0` eligible
seeds. On main, 18-21 of 24 are eligible in each draw.

A change that wiped out boreal snow on most worlds would therefore leave the test passing on 1-5 seeds, and the
test would say nothing about it. That's the ruling working as designed ("rules need not fire where the prerequisites
aren't there"). Other tests (the climate's snow and Earth checks) should catch a world without snow.

Good enough for now. For the quality pass, decide one of these:
- add a floor (for example, at least half of SEEDS4 eligible: a new number);
- or print a warning when the eligible count drops well below main's 18-21.

## Updates
- 2026-10-23: Created from inbox draft draft-forest-test-eligible-floor.md (found by tests-multiseed-rulings).
