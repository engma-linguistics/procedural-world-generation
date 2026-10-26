---
title: "Plume degassing is only ~2% of the carbon source (max ~5%) because the modelled plume melt is small next to the ridges; the literature puts plume CO2 near the ridges' order"
type: task
status: todo
parent: PW-244
milestone: v1
subsystem: tectonics
effort: s
impact: low
found_by: v1-finish-13
blocked_by: []
relates: [PW-875]
refs: [planet/tectonics/earth.py, planet/tectonics/volcanism.py, docs/review/base-climate/v1-finish-13/README.md]
---

## Description
PW-875 adds plume degassing (v1-finish-13, 1b52cdf): the melt of plume heads, vents and aprons times PLUME_CO2.
PLUME_CO2 is 3.3x the ridges' CO2 per km3 (~0.5 wt% against MORB's ~0.15 wt%; Self et al. 2006, Black & Gibson
2019, Marty & Tolstikhin 1998, Crisp 1984).

Smoke run, seed 11, L6, 400 Myr: plumes are a median 1.8% of the source (10-90% 0.8-3.2%, max 4.6%). Earth's
intraplate and plume magma is ~2-3 km3/yr against the ridges' ~21 km3/yr (Crisp 1984). With the 3.3x yield that is
~30% of the ridges' CO2, and Marty & Tolstikhin give plumes ~3e12 mol C/yr against ridges ~2.2e12, with wide error.
So either the modelled plume melt volume is ~5-10x below Earth's, or the source's ridge and arc terms are larger
than their km3 suggest. The arc term is 20 x arc growth in model units.

Measure before changing anything, and don't tune PLUME_CO2:
- [ ] Log per step the ridge, arc and plume parts of source_raw separately, in km3/yr equivalents.
- [ ] Compare plume melt km3/yr with Crisp 1984 (and LIP pulses with Bryan & Ernst 2008's ~1e6 km3 per LIP).
- [ ] If the melt volume is low, that is a volcanism.hotspots calibration question (hotspot count, strength),
  which goes to its own ticket.
