---
title: Salt sources can only be checked against real interiors coarsely - the Earth world has no evaporite or sediment rock, and tundra stays far
type: task
status: todo
parent: PW-692
milestone: v2
subsystem: timezoom
effort: xs
impact: low
found_by: fun10
blocked_by: []
relates: [PW-746, PW-732]
refs: [planet/lineages/seafood.py, "world 506694"]
---

## Description
PW-746 added playas, basin brine springs and mineral licks (mean land distance to salt on Earth 1028 -> 304 km). Caveats for whoever tunes it next: Earth world 506694's `surface_rock` holds only craton and shale (ids 5 and 8) and `sediment_cover` is 0.02 or 2.0, so brines and licks are checked there only as "shale everywhere"; the Amazon (13 km) is that artefact and the generated worlds with real rock mixes are the test. Tundra (Earth 422 km) and the Great Plains (383 km) are still the farthest regions: arctic peoples took salt in meat and blood and from the sea, which the brief does not say. Plant ash is deliberately still a marker. Worth a pass on a generated world with limestone, sandstone and evaporite cover once a showcase run exists.
