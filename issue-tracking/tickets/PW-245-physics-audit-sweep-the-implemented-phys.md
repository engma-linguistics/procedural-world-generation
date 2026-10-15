---
id: PW-245
title: "Physics audit: sweep the implemented physics for weird, wrong or KPI-chasing shortcuts"
type: story
status: todo
parent: PW-244
subsystem: infra
effort: l
impact: high
found_by: daniel
blocked_by: []
relates: []
refs: []
created: 2026-10-15
updated: 2026-10-15
---

## Description
Owner (2026-10-15), high priority. Much of the model was built by agents tuning toward metrics (Earth checks, scorecard, targets in tickets). An agent chasing a number can take a shortcut that hits it for the wrong reason: hard clamps or caps standing in for a process, region- or latitude-specific fudges, special cases keyed to Earth, double-counted or sign-flipped terms, magic constants without a physical basis, units that don't add up, tests loosened to pass, masks instead of processes, terms that only exist to cancel another term. The owner isn't aware of any; runs look better and better; this is a once-over. Method: per subsystem (tectonics/crust/isostasy, surface/erosion, hydrology/lakes, climate/rain/clouds, ocean, ice/icemass/timezoom, vegetation, coast/waves/tides, zoom synthesis, finish), read the code against docs/overview.md and the real-world analogue it claims; list every clamp, cap, clip, fudge factor and Earth-specific branch with its justification or lack of one; check conservation (water, crust volume, sediment, energy where relevant) and units; check git history for tolerance changes in tests. Output: a findings report under docs/review/ (each finding: what, where, why suspicious, severity, suggested proper fix) plus inbox drafts for real problems. Fix only trivial ones in the audit; the rest become tickets. Best done by agents that didn't write the code, one per subsystem, with a coordinator pass to rank the findings.

## Updates
- 2026-10-15: Created.
