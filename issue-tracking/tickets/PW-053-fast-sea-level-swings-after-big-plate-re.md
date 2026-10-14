---
id: PW-053
title: Fast sea-level swings after big plate reorganisations
type: task
status: todo
parent: null
subsystem: tectonics
effort: m
impact: high
found_by: l7jumps
blocked_by: []
relates: []
refs: ["run fe7144", "run 103c05", "run 796a25", "run 07fb28", docs/review/overnight_runs.md, planet/tectonics/earth.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
After the l7jumps fix, sudden land changes are rarer but not gone: L7 fe7144 40→30% land at ~1140 Myr,
back to 34% by 1172; L7 103c05 30→24% at 1376, 27% by 1408; L6 796a25 37→30% at 1320, 34% by 1364; L6
seed 14 (07fb28) 55→49% at 716. Probably any big reorganisation renews ocean floor quickly (ridge age →
mean depth → sea level), plus low L7 continents. Consider limiting how fast mean ocean depth can change
(ridge volume responds over ~10s of Myr), or check the thermostat.

## Updates
- 2026-10-14: Migrated. Merged: Known issue 'Fast sea-level swings remain' (l7jumps), overnight_runs.md 'Final code' concerns, morning_report biggest problem 1.
