---
title: "Earth world: cell-mean hollows on small rivers still hold big lakes (Yakutia 223k km2, Amur 174k km2)"
type: task
status: todo
parent: null
subsystem: hydrology
effort: s
impact: low
found_by: hydro
blocked_by: []
relates: [PW-201, PW-055]
refs: [tools/earth_world.py, planet/hydrology.py]
---

## Description
After PW-055's outlet cut the L6 Earth world's lakes are 2.4 Mkm2 (was 6.1): the Amazon, Congo, Orinoco
and West Siberian "lakes" drain, the Great Lakes, Victoria, Aral and Makgadikgadi stay. Left over: open
lakes in cell-mean hollows on rivers too small for the cut to drain them: lower Lena / Yakutia (69.7 N
124.6 E, 223k km2, 110 m deep, outflow 2300 m3/s through a coastal range cell 209 m high whose river is at
sea level) and the middle Amur (48.1 N 133.7 E, 174k km2, 185 m, 5000 m3/s); also Chad 59k km2 as open
(Q from the model's too-wet Sahel). The valley a river runs in below a cell's mean is deeper in rugged
cells than in flat ones; a cut that also grows with the outlet cell's relief (e.g. x (1 + relief / 50 m))
would drain these but also cut the Great Lakes' outlets (relief 25-37 m), so it needs care.
