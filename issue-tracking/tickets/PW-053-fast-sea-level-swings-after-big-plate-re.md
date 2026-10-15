---
id: PW-053
title: Fast sea-level swings after big plate reorganisations
type: task
status: done
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
- 2026-10-14: Status todo -> done. tectsea 0fd35e5: drivers were (1) the starting ocean (mean age ~90 Myr, no young floor) renewing itself in the first ~100 Myr: sea at the +250 m clamp for ~100 Myr, the land drop at t=0 (abcdac 34->23%); (2) mean ocean age swinging fast with spreading that stops/restarts within a few steps (plate count collapses, sutures, rifts): basin part up to 15-18 m/Myr; (3) land ice (up to -340 m; draft). hot_sea is 0 at default heat_start. Fix: depth_ridge follows mean depth over ridge_time = 30 Myr, tanh limit at 250 m instead of the clip, equilibrium start ages (mean 60). L6 4 seeds x 1 Gyr (1/2/11/21), sea sd 126/195/167/143 -> 124/130/110/89 m, tect clamp samples 22/38/29/20 -> 0, max 20-Myr swing 211/229/334/238 -> 138/264/190/120 (the 264/190 are ice), basin part max rate 15-18 -> 5-8 m/Myr, 4-pt land drops 0/0/0/1 -> 0. L7 s21 (abcdac -> cac9c4): sd 190 -> 173 (sea fix alone 103), frames at +250 20 -> 0, max 20-Myr swing 291 -> 180, land drops 3 -> 1 (12 Myr, initial breakup, 4.4 pts), land range 22-39 -> 28-39%. Leftovers: drafts on ice volume and the L7 late plate collapse.
- 2026-10-14: Migrated. Merged: Known issue 'Fast sea-level swings remain' (l7jumps), overnight_runs.md 'Final code' concerns, morning_report biggest problem 1.
