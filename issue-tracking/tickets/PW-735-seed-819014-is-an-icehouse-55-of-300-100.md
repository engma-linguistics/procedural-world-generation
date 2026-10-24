---
id: PW-735
title: Seed 819014 is an icehouse 55% of 300-1000 Myr at L6 and 75-89% (always-icebox) at L7 even after PW-725
type: task
status: todo
parent: PW-244
milestone: v2
subsystem: climate
effort: s
impact: low
found_by: v1-finish-3
blocked_by: []
relates: [PW-725, PW-202]
refs: [docs/review/base-climate/v1-finish-3/, tools/ice_criteria.py]
created: 2026-10-24
updated: 2026-10-24
---

## Description
After PW-725 (the margin band in km) the L7 pass rate on the four old showcase seeds is 5/8 seed-draws with the
same icehouse median as L6 (33%). One seed, 819014, stays icy on both levels and both draws: L6 55% (fails), L7
89% and 75% icehouse with ice below -150 m on 52% / 30% of updates (always-icebox). The bar allows outliers, so
this is not a v1 blocker; worth one look (ice_diag on it: CO2 term vs albedo, where its sheets sit, its relief) if
a later sweep shows more seeds like it, i.e. if it is a class of geography rather than one planet.

## Updates
- 2026-10-24: Created from inbox draft draft-seed-819014-icy-at-both-levels.md (found by v1-finish-3).
