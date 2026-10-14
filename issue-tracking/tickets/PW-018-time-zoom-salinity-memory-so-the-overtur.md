---
id: PW-018
title: "Time zoom: salinity memory so the overturning can stay off (Heinrich, Younger Dryas)"
type: story
status: todo
parent: PW-013
subsystem: timezoom
effort: l
impact: med
found_by: daniel
blocked_by: []
relates: [PW-030]
refs: [planet/timezoom.py, planet/ocean.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
In the time zoom, meltwater pulses should be able to weaken or shut down the overturning for
centuries to millennia (Heinrich events, Younger Dryas). Today the overturning has no memory of its
salinity: after hosing it recovers within 2–3 climate updates. Carry salinity between climate
refreshes so off-states persist. The meltwater link exists already (each full climate gets the net
ice loss as `melt`), but over Earth's first 150 kyr it is only ~0.03 Sv. Linked to the missing
100-kyr cycle.

## Updates
- 2026-10-14: Created from the rain/overturning epic (owner discussion 2026-10-14).
