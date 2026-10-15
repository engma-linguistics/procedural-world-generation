---
id: PW-236
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
refs: [tools/earth_world.py, planet/hydrology.py, tools/earth_data.py]
created: 2026-10-15
updated: 2026-10-15
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

## Updates
- 2026-10-15: Hydro2: general fixes drain real lakes first; needs river-conditioned outlet heights for the Earth world (merged draft).
- 2026-10-15: Merged inbox draft draft-earth-gorge-lakes.md ("Earth world: gorge rivers (Lena, Amur, Danube Iron Gates, Yangtze Three Gorges, Columbia) leave cell-mean dams and fake lakes", found by hydro2).
  Follow-up of PW-236 (not fixed). On the L6 Earth terrain the leftover fake lakes are all rivers through
  gorges narrower than a cell, whose cell mean stands as a dam: lower Lena / Yakutia (69.7 N 124.6 E,
  223k km2 open), middle Amur (48.1 N 133.7 E, 174k), the Pannonian basin (46.7 N 20.5 E, 107k, closed:
  the Danube's Iron Gates), Sichuan (29.5 N 105.9 E, 54k closed: the Three Gorges), the Columbia, Snake,
  Fraser and Yukon. Tried (hydro2), with the Great Lakes, Victoria and land draining inland as guards:
  - a cut that also grows with the outlet's relief (+ c x mean drop to the lower neighbours): c = 0.5
    drains Yakutia but not the Amur, already takes Lake Michigan away at c = 0.25 and lowers inland
    drainage 12.2% -> 11.2%;
  - a valley floor from the sub-cell ETOPO samples (min or 10th percentile of each cell, the river cut
    down to it, optionally faded in with discharge): drains everything including the Great Lakes, because
    ETOPO holds their bathymetry, so the cell minimum next to a lake is the lake's floor.
  What would work: a river-conditioned sub-cell elevation, i.e. the height where the river leaves each cell
  (HydroSHEDS-style: the lowest ETOPO sample on the cell's boundary that the routed river crosses, or a
  d8 flow-routing on the 1/6 deg ETOPO grid aggregated to cells), used as the outlet height in
  `hydrology.lakes` for the Earth world only. Earth-only data work; generated worlds don't need it (their
  rivers are cut by the run's own erosion).
- 2026-10-15: Created from inbox draft draft-earth-world-leftover-lakes.md (found by hydro).
