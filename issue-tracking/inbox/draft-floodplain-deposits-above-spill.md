---
title: Floodplain deposits on a closed hollow's slopes can still raise cells above the hollow's spill point (~3% of deposition)
type: task
status: todo
parent: PW-245
subsystem: surface
effort: s
impact: low
found_by: surface-hydro
blocked_by: []
relates: [PW-280, PW-054]
refs: [planet/surface.py]
---

## Description
After PW-280 no cell where rivers end (closed lake, closed pit) is filled above its basin's spill point. But
`_route`'s floodplain share (1 - exp(-d / alluvial)) x exp(-slope / 2 m/km) is kept on every gentle land cell
it passes, uncapped, including cells inside a closed hollow near its rim. Measured (L5 seed 1, 300 Myr, cells at
least 1 m below their spill point): 2.8-3.3% of all deposition lands above the cell's spill level (5.1% before
PW-280, when the mounds added to it). On an open plain unlimited aggradation is fine (alluvial plains build up),
but inside a closed hollow it builds the rim up and can deepen or dam the basin.
Simplest sound fix: in a hollow (priority-flood fill above the ground), cap the floodplain keep at the cell's
room below its spill point, as pits are; the excess carries on downstream to the basin floor, where PW-280's
room rule applies.
