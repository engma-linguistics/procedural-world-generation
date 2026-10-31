---
title: Time zooms still take every cell below their moment's sea level for sea, even cut off from the ocean
type: task
status: todo
parent: null
milestone: v2
subsystem: timezoom
effort: s
impact: low
found_by: lane98
blocked_by: []
relates: [PW-1229]
refs: [planet/timezoom/sim.py, planet/geo.py, viewer/globe/load.js]
---

## Description
In plain words: lane 98 (PW-1229) made worlds, runs and the viewer count ground below sea level as sea only when
it reaches the ocean (`geo.is_land`); a pocket cut off from it is land (a lake or a dry depression). The glacial
time zoom keeps its own rule: `timezoom/sim.py` takes a cell as sea where `sl - bed > 0` (line ~416, `sea0`) and
counts the ocean's area as every cell at or below 0 (`ocean_area`, line ~84), so an inland pocket below the moment's
sea level is sea there, and a lowstand can't drain one. The viewer's time-zoom frames skip the new land view too
(`landView` in viewer/globe/load.js returns early for time zooms).
What I'd try: build the time zoom's sea mask with `geo.is_land(bed - sl, ice, grid)` once per step (or per kyr
chunk: cost ~20 ms at L7), and let `landView` apply `seaMask` to time-zoom frames on `elevation - ice` vs 0.
- [ ] a time zoom of a world with a cut-off pocket keeps it land at every frame
