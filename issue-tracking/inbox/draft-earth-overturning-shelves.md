---
title: Earth's North Atlantic overturning falls 15 -> 10 Sv when the Antarctic ice shelves become sea
type: task
status: todo
parent: null
subsystem: ocean
effort: s
impact: med
found_by: pw354-earth-bed
blocked_by: []
relates: [PW-354]
refs: [planet/ocean.py, tools/earth_data.py, "docs/overview.md §2.7"]
---

## Description
PW-354 made `tools/earth_data.py` take ETOPO1's floating ice shelves (Ross, Ronne-Filchner, Amery;
~1.15 million km2, 92 L6 cells) as sea instead of land with a 1 m bed. On the L6 Earth world the
overturning (`meta.overturning`) then falls from 16.9 to 12.6 Sv, and almost all of it in the
north: the North Atlantic site 14.9 -> 10.0 Sv (its area 4.97 -> 4.18 million km2), while the
southern sinking grows only 1.9 -> 2.6 Sv. The true bed alone changes nothing (16.93 Sv; measured
by restoring the old shelf cells on the new data). Knock-ons: Norway W waves 52 -> 41 kW/m,
Reykjavik -1.1 C, 60-70N sea -0.4 C.

The north's deep-water formation shouldn't hinge on the shelves 12,000 km away. Suspects:
`ocean.salinity` holds the sea's area-mean salinity at S0 (adding brine-heavy shelf sea next to
Antarctica would freshen everything else relative to it), or the density contrast is taken
against a global mean. Check which, and whether the response is physical (more AABW does compete
with NADW on Earth, but not by a third through the surface salinity alone).
- [ ] find the path by which the shelves set the north's sinking (salinity normalisation, density reference)
- [ ] decide whether it is sound; if not, fix it in the ocean model (not by putting the shelves back)
