---
title: The L6 Earth world floods ~6 Mkm2 of flat basins as lakes (Amazon, Congo, Yakutia)
type: task
status: todo
parent: null
subsystem: hydrology
effort: s
impact: med
found_by: veg
blocked_by: []
relates: [PW-110, PW-122]
refs: [tools/earth_world.py, "world fe2af4", "world dc3732"]
---

## Description
The Earth reference world (tools/earth_world.py, erosion off) has 492 lake cells at L6, ~6 Mkm2 (Earth's lakes ~2.5 Mkm2): much of the central Amazon (cell at -3,-60: lake level 73 m over ground at 38 m), the Congo cuvette (a 106 m deep "lake"), Yakutia. With erosion off, 110 km cell means leave flat basins as pits that the lake fill keeps. These cells show as lakes in the biome and vegetation maps (no rainforest in the central Amazon on the Earth world). tools/veg_check.py ignores lakes and computes vegetation on every land cell. Fix in the Earth world's hydrology (e.g. a light carving pass, or a stricter MIN_SLOPE for the Earth world).
