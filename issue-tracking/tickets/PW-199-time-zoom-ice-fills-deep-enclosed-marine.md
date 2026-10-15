---
id: PW-199
title: "Time zoom: ice fills deep enclosed marine basins to 11-12 km thick"
type: task
status: todo
parent: null
subsystem: timezoom
effort: s
impact: low
found_by: finish
blocked_by: []
relates: [PW-031, PW-189]
refs: [planet/timezoom.py, "run ee65aa", "run:ee65aa@632Myr(70.8,123.3)"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
On run ee65aa @ 632 Myr (L6) the thickest time-zoom ice is 11.6-11.8 km, in a few cells whose
bed starts ~4 km below sea level and is ringed by 4-5 km land (e.g. 70.8 N, 123.3 E; also 74.9 N,
45.8 E): ice flows in from the surrounding sheets, grounds, and the bed sinks another 0.3 x H.
Since PW-031 these hardly lower the sea any more (only the ice above flotation counts), but the
"thickest" stat and the finished world (bed floored at 1 m, ice to the surface) look odd.
Probably an enclosed deep basin the grid can't resolve (a trench next to land). Try: calving or
breaking off grounded ice deeper than ~1-2 km of water even without an open-sea neighbour, or
let such basins float the ice (shelf).

## Updates
- 2026-10-14: Created from inbox draft draft-timezoom-deep-basin-ice.md (found by finish).
