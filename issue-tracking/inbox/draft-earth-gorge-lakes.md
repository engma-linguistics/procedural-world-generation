---
title: "Earth world: gorge rivers (Lena, Amur, Danube Iron Gates, Yangtze Three Gorges, Columbia) leave cell-mean dams and fake lakes"
type: task
status: todo
parent: null
subsystem: hydrology
effort: m
impact: low
found_by: hydro2
blocked_by: []
relates: [PW-236, PW-201]
refs: [tools/earth_data.py, tools/earth_world.py, planet/hydrology.py]
---

## Description
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
