---
id: PW-1331
title: "Wet tropical forest grows ~0.55x the measured NPP: its photosynthesis is low (EPS_SCALE cut to hide the grasses' surplus)"
type: task
status: todo
parent: null
milestone: later
subsystem: surface
effort: m
impact: med
found_by: lane123
blocked_by: []
relates: [PW-1261, PW-228, PW-806]
refs: ["planet/vegetation.py::_year", "planet/vegetation.py::EPS_SCALE", "planet/vegetation.py::_TUNE", "planet/vegetation.py::potential", tools/veg_check.py, docs/review/vegetation/npp-check/diagnosis.md, docs/review/vegetation/npp-check/npp_check.py, docs/review/vegetation/npp-check/pft_probe.py, "Malhi, Doughty & Galbraith 2011 Phil Trans R Soc B 366:3225, PMC3179639, Table 3", "MOD17A3 (tools/earth_data.py::earth_mod17_npp)", "world 506694 (Earth L6)"]
created: 2026-11-02
updated: 2026-11-03
---

## Description
**In plain words.** On Earth's observed climate the model's rainforest grows about half of what field plots measure
(~630 g C/m2/yr against a median ~1160 for 17 lowland tropical plots in Malhi et al. 2011, Table 3; Miami ~1000-1100,
MOD17 ~920-1010). Its carbon-use efficiency is right (NPP/GPP 0.33-0.36); its GPP is low (TrBE 2012 g C/m2/yr at optimum
LAI 3.4; field GPP for Amazonian forest is ~3000+, not read here: read a source first). The global efficiency cut
EPS_SCALE = 0.8 was tuned on Earth's land NPP total, which the grasses' too-high carbon-use efficiency inflated (fixed in
lane 123, PW-1261): the two errors cancelled in the total.

Screens (lane 123, Earth L6 observed climate): tropical trees' efficiency x1.3 brings wet-tropics NPP to ~925-1010 and
land NPP to 60.5 Pg (with the herbs' fix) but shrinks savanna from 17.7 to 13.8 Mkm2 (target band 13-27; African
900-1200 mm savanna turns forest): the savanna-forest balance and fire need checking with it. All efficiencies x1.25
(EPS_SCALE 1.0) overshoots temperate and cold land (T 10-18 C, 1000-1500 mm: 1070 against Miami 734 / MOD17 741).
- [ ] read a measured tropical light-use efficiency (or GPP vs absorbed PAR) and check the light under the observed cloud
- [ ] fix the tropical GPP step; re-check savanna area, fire and potveg agreement (tools/veg_check.py)

## Updates
- 2026-11-03: Milestones 11-03: v2 -> later: physics side track, ranked 3; gates no tag (plant growth, with PW-1261 and PW-1332)
- 2026-11-02: Created from inbox draft draft-tropical-forest-gpp-low.md (found by lane123).
