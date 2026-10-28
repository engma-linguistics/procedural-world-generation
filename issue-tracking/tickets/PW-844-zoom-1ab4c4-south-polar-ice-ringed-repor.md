---
id: PW-844
title: Zoom 1ab4c4 (south polar, ice-ringed) reports 8 harbours but none show and none are expected
type: task
status: done
parent: PW-244
milestone: v1
subsystem: zoom
effort: s
impact: low
found_by: owner-feedback-2026-10-25
blocked_by: []
relates: []
refs: []
created: 2026-10-25
updated: 2026-10-28
---

## Description
Owner feedback 2026-10-25 (feedback doc on world 2a7385): Count source being checked.

## Updates
- 2026-10-28: Status todo -> done. Lane 21: (1) zoom sea floor held within the coarse cells' range less its detail, and a sea cell the fine coast leaves mostly land no longer held to its mean (zoom 1ab4c4: -23,128 m -> -4,690 m); (2) humanuse.open_sea: a zoom's harbours need water joined to its edge or a sea >= 50 km square (581 harbour px -> 0). Before/after: docs/review/zoom/pw844/. The world's enclosed deep sea cells: inbox draft.
- 2026-10-25: Diagnosis: one isolated coarse cell at -4393 m among 2.7-3.5 km high ground is read as sea; zoom interpolation overshoots it to -23 km (deeper than any world cell); harbour test has no check for an enclosed pit or a sea frozen ~8 months. Raised to v1: the depth overshoot is a physical bug.
- 2026-10-25: Created.
