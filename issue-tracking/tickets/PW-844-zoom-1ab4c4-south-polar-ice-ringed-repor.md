---
id: PW-844
title: Zoom 1ab4c4 (south polar, ice-ringed) reports 8 harbours but none show and none are expected
type: task
status: todo
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
updated: 2026-10-25
---

## Description
Owner feedback 2026-10-25 (feedback doc on world 2a7385): Count source being checked.

## Updates
- 2026-10-25: Diagnosis: one isolated coarse cell at -4393 m among 2.7-3.5 km high ground is read as sea; zoom interpolation overshoots it to -23 km (deeper than any world cell); harbour test has no check for an enclosed pit or a sea frozen ~8 months. Raised to v1: the depth overshoot is a physical bug.
- 2026-10-25: Created.
