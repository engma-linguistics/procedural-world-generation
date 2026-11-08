---
id: PW-1517
title: "Rainforest keeps too much of what it fixes: NPP/GPP ~0.45 against ~0.30 measured"
type: task
status: wontdo
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
- 2026-11-08: Status todo -> wontdo. Coordinator 11-08: closed within the measured range (scout 217). NPP/GPP 0.445 sits inside Malhi 2009's 0.32-0.49; wood+root upkeep matches Chambers 2004 (1.02x). The real gap (top-leaf rate 1/1.6 of Chambers, needing a diffuse-light GPP gain) is filed later/low as the diffuse-light ticket. Stable, not fiddly.
- 2026-11-08: Scout 217 (pass 1, docs/review/climate/npp/scout3.md): the suspect is cleared. Wood+root upkeep (rw maintenance 716 + 66% of growth resp ~993 g C/m2/yr) matches Chambers et al. 2004's measured Manaus stems 420 + roots 550 = 970; rw x1.5 would overshoot by ~31% and cut wet-tropics NPP 1012 -> 854. The low term is the leaves: ~575 against 710 (Chambers' rate on the model's KN 0.15 profile) to 980 (as published); top-leaf rate 0.33 umol/m2/s at 25 C against Chambers' in-situ 0.54 (x1.6) and Atkin et al. 2015's outer-canopy 0.82 (x2.5). Raising rl alone makes the LAI rule keep fewer leaves (4.58 -> 4.11 at x1.5, measured 4.7-5.1) and cuts NPP 10%; keeping NPP needs GPP +6% (x1.5) / +12% (x2.0), a canopy LUE of 1.23 / 1.31 g C/MJ, inside Yan et al. 2017's K67 diffuse-light span (1.1-1.9). NPP/GPP 0.445 is already inside Malhi et al. 2009's measured 0.32/0.34/0.49 (the ~0.30 is the poor-soil end). Recommendation: no rw change; either close as within range, or the next pass builds a diffuse-light gain (inbox draft) and pairs it with TrBE rl x1.5 (Chambers). Not an eps stand-in. No coupled screen run (only buildable arm was the stand-in). Baseline main cb8374b0, Earth L6 world 506694, observed climate.
- 2026-11-08: Created from inbox draft draft-tropical-forest-cue-high.md (found by scout210).
