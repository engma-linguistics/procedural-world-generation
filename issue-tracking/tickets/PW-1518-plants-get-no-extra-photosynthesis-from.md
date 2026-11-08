---
id: PW-1518
title: Plants get no extra photosynthesis from diffuse (cloudy-sky) light; the rainforest's leaf upkeep waits on it
type: task
status: todo
parent: null
milestone: later
subsystem: surface
effort: m
impact: low
found_by: scout217
blocked_by: []
relates: [PW-1517, PW-1331]
refs: ["planet/vegetation.py::_year", "planet/vegetation.py::_TUNE (TrBE eps 1.43)", "planet/vegetation.py::KN_RESP", "planet/climate.py::shade_from_hours", docs/review/climate/npp/scout3.md, docs/review/climate/npp/scout3_probe.py, docs/review/climate/npp/scout3/, docs/review/climate/npp/scout2.md, docs/review/vegetation/npp-check/npp_check.py, "Yan et al. 2017 JGR Biogeosci 122:3014 doi:10.1002/2017JG004008 (White Rose eprint 124617)", "Chambers et al. 2004 Ecol Appl 14:S72 (Table 2)", "Atkin et al. 2015 New Phytol 206:614", "Malhi et al. 2009 GCB 15:1255", "world 506694 (Earth L6)"]
created: 2026-11-08
updated: 2026-11-08
---

## Description
**In plain words.** Under cloud, sunlight comes from the whole sky and reaches the shaded inner leaves of a forest.
Amazon towers fix 1.1 g of carbon per MJ of absorbed light in the sunny dry season, and up to 1.9 under the wet
season's cloud (Yan et al. 2017, K67 Tapajos). The model's plants get the same efficiency whatever the sky. Because of
that, scout 210 had to take the dry-season floor for the rainforest tree (TrBE eps 1.43, i.e. 1.14 g C/MJ). Scout 217
found that the rainforest's leaves breathe too little: about 575 g C/m2/yr against 710-980 measured at Manaus
(Chambers et al. 2004), and a top-leaf rate x1.6 under Chambers' in-situ rate. The measured fix (TrBE rl x1.5) cannot
go in alone. The model would keep fewer leaf layers (LAI 4.58 -> 4.11, measured 4.7-5.1) and wet-tropics NPP would fall
10% (1012 -> 910 g C/m2/yr, satellite 1011). The missing photosynthesis (+6%, a canopy efficiency of 1.23 g C/MJ, i.e.
Df ~0.61 on K67's span) is what a diffuse-light gain supplies.

What misleads if never done: the rainforest's respiration stays about 20-40% under the measured leaf upkeep, and any
carbon read-out that splits GPP into respiration and growth is off. Cloudy and sunny climates also grow the same per
unit of light, so a cloudier world's forests are under-credited. The impact is low: the rainforest's NPP and NPP/GPP
(0.445, measured 0.32-0.49) are inside the measured ranges today.

- [ ] derive a monthly diffuse fraction Df from the model's cloud (the shade the PAR already uses), as Yan et al. did
  from the sky clearness index
- [ ] a two-leaf or Df-linear efficiency for trees (Yan: sunlit 1.11, shaded 4.35 x (0.25 + 0.75 Df^1.8) g C/MJ), with
  the clear-sky floor kept at today's eps; check whether the optimal LAI rises toward the measured 4.7-5.1
- [ ] then TrBE rl x1.5 (Chambers' in-situ canopy leaf rate 0.54 umol/m2/s against the model's 0.33 at 25 C)
- [ ] Earth screens with scout3_probe.py and npp_check.py: wet-tropics NPP near 1011-1160, LAI, NPP/GPP; temperate
  boxes against MOD17 if the gain applies to all trees (EPS_SCALE is fitted there)
- [ ] then an 8-draw L6 screen, then the 36-draw judge

## Updates
- 2026-11-08: Created from inbox draft draft-diffuse-light-gain.md (found by scout217).
