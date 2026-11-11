---
id: PW-1683
title: At L7 land above 3 km runs ~4.3% late in a 1 Gyr run (Earth 2.5% on the L7 grid); L7 continents ~2 km thicker than L6's
type: task
status: todo
parent: null
milestone: v1.0
subsystem: tectonics
effort: m
impact: med
found_by: lane 286
blocked_by: []
relates: [PW-1497, PW-1446]
refs: [docs/review/tectonics/andes-late.md, docs/review/tectonics/mountains/andes_late_series.py, docs/review/tectonics/mountains/scout7_measure.py, "planet/tectonics/crust.py::flow_and_orogeny", "planet/tectonics/crust.py::andean_contraction", "planet/tectonics/crust.py::thermostats", data/earth/L7.npz, "Amante & Eakins 2009 (ETOPO1)"]
created: 2026-11-10
updated: 2026-11-10
---

## Description
In plain words: on the showcase grid (L7), a 1 Gyr test planet has about 1.7 times Earth's share of land above 3 km
in the second half of its run, though land above 4 km is Earth-like. If never checked, the December 1-2 Gyr L7
showcase planets may show broad 3-4 km plateaus more often than Earth does, and nobody will know whether the new
Andean physics or the L7 grid causes it.

Numbers (lane 286, andes-late.md section 3; L7 seed 2, 1 Gyr, main 7dae542a defaults, scratch run deleted):
median over 20-Myr checkpoints, 600-1000 Myr, land above 3 km 4.33% (mean 4.01%), above 4 km 1.29%; Earth on the
L7 grid (ETOPO1 bedrock, data/earth/L7.npz) 2.5% and 1.6%. Mean continental crust late 36.9 km, against 34.9 km on
the L6 run of the same seed and code. At L6 the Andean change makes no such difference (three seeds, 600-1000 Myr:
land above 3 km 2.69% with it, 3.17% without), but there is no L7 run without it.

What to try: one L7 seed-2 1 Gyr run with `andean_shortening=0 collapse=0` on the same commit, and one more L7 seed
each way if they differ; `andes_late_series.py` on both. If the L7 excess is the grid's (thicker continents at L7),
look at what sets mean continental thickness per level (the volume/area thermostats, `crust_flow` substeps at
L7, the height cap) rather than at the mountains.
- [ ] L7 off-arm run(s) measured against the on-arm numbers above
- [ ] cause named (PW-1497's, or L7's own), with a fix or a reason it is within bounds

## Updates
- 2026-11-10: Created from inbox draft draft-l7-land-above-3km.md (found by lane 286).
