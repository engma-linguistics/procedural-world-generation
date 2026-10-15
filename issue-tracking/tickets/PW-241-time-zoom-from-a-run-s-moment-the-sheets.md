---
id: PW-241
title: "Time zoom from a run's moment: the sheets still thicken and spread onto shelves at first (~-70 m in 15 kyr in a cold era)"
type: task
status: todo
parent: null
subsystem: timezoom
effort: m
impact: low
found_by: icemb
blocked_by: []
relates: [PW-190, PW-115]
refs: [planet/tectonics/earth.py, planet/timezoom.py]
created: 2026-10-15
updated: 2026-10-15
---

## Description
After PW-190 (icemb) the run's ice is the shared mass balance's extent, so a time zoom starts close to
its own balance. What's left, measured on seed 3199 @ 736 Myr (L6, dT -6, run ice 10.7%, sea level
from ice -243 m) with the orbit, CO2 and ice albedo off (pure consistency): the time zoom falls -72 m in
the first ~15 kyr and then stays. At the start its snow gains +16,400 Gt/yr against 4,600 Gt/yr of melt
and 6,400 of calving (the run's own accounting: +15,100 / -6,500 Gt/yr and ~6,000 of calving); after
20 kyr its old ice is ~185 m thicker (Nye profile at 50 kPa vs the time zoom's shallow-ice profile), it
covers 640 more land cells (+13 Mkm3) and grounds on 440 shelf cells (+4 Mkm3, median 540 m deep).
Options: a thicker Nye profile (ICE_TAU) to match the time zoom's flow; let the run's sheets ground on
shallow shelves as the time zoom's do; or a short spin-up in the time zoom. Each makes the run's ice a
little bigger.

## Updates
- 2026-10-15: Created from inbox draft draft-timezoom-start-drift.md (found by icemb).
