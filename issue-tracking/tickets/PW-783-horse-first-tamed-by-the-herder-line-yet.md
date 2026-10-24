---
id: PW-783
title: Horse first tamed by the herder line yet herders end with 0% use (fake world, tree seed 4)
type: task
status: todo
parent: PW-103
milestone: v2
subsystem: timezoom
effort: s
impact: low
found_by: fun19
blocked_by: []
relates: [PW-782]
refs: [tests/test_lineages.py]
created: 2026-10-24
updated: 2026-10-24
---

## Description
In `test_horses_are_tamed_where_herders_meet_the_wild_range_and_riding_spreads` (made multi-seed for PW-782), seed 4 tames the
horse 10.7 kyr ago with line `herd` as first tamer, but at the end `users_share` is herd 0.0 vs farm 0.62. A tamer whose own
people never use the animal looks wrong (the herd line may have lost its ground, or use is counted by presence). The test now
asserts herders ride (>0.5) in a majority of the seeds that tame, not in every one. Check whether this is a real bug or a fixture artifact.

## Updates
- 2026-10-24: fun20: not a bug. Seed 4's herd line is squeezed by the farmers from 106 to 3 Mkm2 between 28 kyr ago and now (farm 91 -> 186 Mkm2) and ends as 6 cells on a second landmass the horse never reached, so its presence-weighted use is 0 while the farmers' is 0.62. Test now asserts the precise condition (herders on the horse's landmass at the end ride >0.5; a line driven off it rides 0).
- 2026-10-24: Created from inbox draft draft-herd-tamer-no-riders.md (found by fun19).
