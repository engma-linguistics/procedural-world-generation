---
title: Check an Earth time zoom's start on the true Antarctic bed
type: task
status: todo
parent: null
subsystem: timezoom
effort: s
impact: low
found_by: pw354-earth-bed
blocked_by: []
relates: [PW-354]
refs: [planet/timezoom.py, tools/earth_data.py]
---

## Description
Since PW-354 `timezoom.source_earth` gets ETOPO1's true bed (below the sea under 418 of 1003
Antarctic and 17 of 133 Greenland ice cells at L6, down to -1670 m) and no shelves (they are sea
in the data now), so its old shelf rule (thin ice on a floored bed -> sea at -500 m) is gone and
land is `geo.is_land`. Not run since: an Earth time zoom (e.g. 100 kyr at L6) should start with
its sheets grounded where the data has them (its flotation test, bed + H > sl + (1 - rho_i/rho_w) H,
may unground a few cell-mean grounding-line cells that the sample-level test kept), and its sea
level and ice volume (Antarctica ~24.8 million km3 of ice now, was 22.9 with the floored bed)
should start near today's.
- [ ] run an L6 Earth time zoom of ~100 kyr; compare its first frames' ice extent, volume and sea level with before
