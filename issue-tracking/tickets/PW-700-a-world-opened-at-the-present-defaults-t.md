---
id: PW-700
title: A world opened 'at the present' defaults to an interglacial within the present icehouse era, when one exists
type: task
status: done
parent: PW-244
milestone: v1
subsystem: highlights
effort: s
impact: med
found_by: daniel
blocked_by: []
relates: []
refs: []
created: 2026-10-23
updated: 2026-10-23
---

## Description
Owner (2026-10-24): when a run's present falls mid-icehouse, the default 'present' world should be a warm moment of that era (like Holocene Earth) when the run or its time zoom has one; full-glacial moments stay reachable through the time zoom. Today highlights.representative_time picks the default moment (waiting for the full flora, PW-634). Pick the interglacial from the run's own glacial-interglacial record (or the time zoom's), never from a fixed date.

## Updates
- 2026-10-23: Status todo -> done. Lane v1-finish-2 (5e552b9): highlights.representative_time moves a pick inside an icehouse era (sea_ice_m <= -20 m, spells within 8 Myr joined) to the era's least-ice quarter, the geographically most typical of those; planet make's time zoom then starts there and finishes at its latest interglacial (finish.now_kyr). From the run's own record, no fixed date. Test test_representative_time_interglacial_in_icehouse.
- 2026-10-23: Created.
