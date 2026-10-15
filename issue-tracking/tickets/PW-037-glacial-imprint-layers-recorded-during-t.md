---
id: PW-037
title: Glacial imprint layers recorded during the time zoom
type: story
status: todo
parent: PW-090
subsystem: timezoom
effort: l
impact: high
found_by: daniel
blocked_by: []
relates: [PW-030, PW-091]
refs: [planet/timezoom.py, planet/timezoom_kernels.py, docs/proposals/glacial_timezoom.md]
created: 2026-10-14
updated: 2026-10-14
---

## Description
While the time zoom runs, record what the ice leaves behind, as layers of the finished world:
- maximum ice extent and thickness;
- glacial erosion depth (U-shaped valleys, cirques, fjords, overdeepened lake basins);
- moraine and till belts at ice margins;
- outwash plains;
- proglacial and ice-dammed lakes (also a termination mechanism for the 100-kyr cycle, PW-030);
- loess thickness downwind of outwash;
- isostatic depression and rebound (the time zoom already sinks bedrock ~0.3× ice thickness).

Glacial erosion and proglacial lakes were "not done" in the original time-zoom spec.

## Updates
- 2026-10-14: PW-189 owns the crustal rebound mechanism; this ticket uses it.
- 2026-10-14: Became story 2 of the world finishing pass PW-090 (owner, 2026-10-14).
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Glacial time zoom ('Not done: glacial erosion, proglacial lakes').
