---
title: Few mid-sized islands (10,000-100,000 km2): 11 on the L8 world vs 44 on Earth at the same grid
type: task
status: todo
parent: null
milestone: v2
subsystem: tectonics
effort: m
impact: low
found_by: lane96
blocked_by: []
relates: [PW-116, PW-117]
refs: [planet/tectonics/crust.py, planet/tectonics/events.py, "world a16f5a", "world 2a7385", docs/review/l8-world/explore.md]
---

## Description
In plain words: the worlds have big continents and plenty of specks, but hardly any islands the size of Sicily to
Iceland or a Japan-sized chain. Those are what make seas interesting to sail and settle.

Counted connected land (lane 96, read-only): a16f5a (L8): 279 landmasses, 169 single-cell, 255 under 10,000 km2,
**11 of 10,000-100,000 km2**, 7 over 1 Mkm2. Earth ETOPO1 resampled to the same L8 grid: 456, 230 single-cell,
392 under 10,000 km2, **44 of 10,000-100,000 km2**. L7 2a7385: 64 landmasses, 4 mid-sized.
So L8 resolves the small end fine (counts near Earth's); the gap is in the middle, which is model, not resolution:
Earth's are mostly microcontinents and rifted slivers (Madagascar-scale is above this band; Sri Lanka,
Tasmania, Sardinia-Corsica, New Caledonia), mature island arcs (Japan, Philippines pieces) and big volcanic islands
(Iceland). Candidate levers: rifting's minimum continental piece (pieces of 0.3-3% of the surface are forbidden,
overview 2.2), island arcs staying blocky (PW-116), hotspot islands sub-cell (PW-117).
Count on a few L7 seeds before acting; one world each is thin.
