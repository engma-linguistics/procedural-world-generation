---
id: PW-1517
title: "Rainforest keeps too much of what it fixes: NPP/GPP ~0.45 against ~0.30 measured"
type: task
status: todo
parent: null
milestone: later
subsystem: surface
effort: m
impact: low
found_by: scout210
blocked_by: []
relates: [PW-1331, PW-1261]
refs: ["planet/vegetation.py::_year", "planet/vegetation.py::_ROWS (TrBE rw, rl)", "planet/vegetation.py::KN_RESP", docs/review/climate/npp/scout2.md, docs/review/climate/npp/scout1.md, "exports/scout210/probe.py (scout 210's worktree, scratch)", "Malhi, Doughty & Galbraith 2011 Phil Trans R Soc B 366:3225 (NPP/GPP ~30% for tropical forest)", "Collalti & Prentice 2019 Tree Physiol doi:10.1093/treephys/tpz034 (forests 0.46 +- 0.12)", "Lloyd et al. 2010 Biogeosciences 7:1833", "world 506694 (Earth L6)"]
created: 2026-11-08
updated: 2026-11-08
---

## Description
**In plain words.** On Earth's observed climate the model's rainforest tree (TrBE) now grows about the right amount
(1016 g C/m2/yr in the wettest tropics, satellite 1011, field ~1160), but it gets there by fixing ~10% too little carbon
(GPP 2815 against ~3100 at the Tapajos tower) and burning too little of it in upkeep: NPP/GPP is 0.45, where tropical
forest measures ~0.30 (Malhi et al. 2011). It was already 0.42 with KN_RESP 0.4 (lane 181); before that ~0.33.

What misleads if never done: anything that reads the rainforest's respiration or GPP (a carbon budget, a future
diffuse-light gain that lifts GPP) will overshoot NPP, because the upkeep that should absorb it is missing. Wood and
root upkeep (rw, flat per stand) is the likely place: the leaf term now follows the measured canopy profile (KN 0.15).

- [ ] read a measured stem + root respiration for Amazon forest (Malhi 2009/2011 components) against rw x Q10
- [ ] if rw is low, raise it with a source and re-check wet-tropics NPP with npp_check.py (needs a matching GPP lift,
  e.g. diffuse-light gain, Yan et al. 2017, or NPP falls back)

## Updates
- 2026-11-08: Created from inbox draft draft-tropical-forest-cue-high.md (found by scout210).
