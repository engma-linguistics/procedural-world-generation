---
title: "End pCO2 spreads 90-990 ppm because the carbon source varies ~2x GEOCARB's degassing: the climate drift (sd 3 C, documented as standing for outgassing among others) rides on top of the explicit tectonic outgassing"
type: task
status: needs-decision
parent: PW-244
milestone: v1
subsystem: climate
effort: s
impact: med
found_by: v1-finish-12
blocked_by: []
relates: [PW-865, PW-819, PW-806]
refs: [planet/tectonics/earth.py, planet/tectonics/params.py, docs/review/base-climate/v1-finish-12/]
---

## Description
Measured on the thermostat-off L6 1 Gyr draws (docs/review/base-climate/v1-finish-12/README.md section 4,
`srcnoise.py`, `endterms.py`, `jointco2.py`):
- **Tectonic outgassing** (ridges + arcs): smooth (lag-1 r 0.97-0.98 per 2 Myr), sd(ln) 0.2-0.45 after 300 Myr.
- **drift_source factor** (climate_drift sd 3 C, 40 Myr): sd(ln) 0.26-0.40.
- **Total source**: sd(ln) 0.35-0.61. GEOCARB's f_G spans ~0.75-1.75 over the Phanerozoic, an sd(ln) of ~0.2-0.25.
- **What the CO2 does with it**: the planted law's gain is 1/(a + cG) ~ 1.8 e-folds of CO2 per e-fold of source.
  So sd(ln pCO2) is 0.95-1.37, and the end pCO2 lands anywhere from 90 to 990 ppm.
- **The lag is not it**: solving CO2 jointly with the climate it gives narrows the spread by only ~5%.
- **Cost**: two of ten draws end at ~90 ppm with C3-starved, treeless wet tropics (3%, 13%).

params.climate_drift's own comment says the drift stands for "outgassing and all the burial/ocean details the model
doesn't have". The outgassing part is now explicit, so it counts twice.

Options:
- A. Size the drift for what the model lacks (organic burial, ocean chemistry), with the explicit outgassing's
  measured variance taken out: e.g. drift sd so that the total source sd(ln) ~0.25-0.3. That would be a drift of
  ~1.5-2 C; it needs a literature number for the non-degassing part (f_org/burial variability).
- B. Keep it. Earth's own Phanerozoic CO2 spans 200-4000 ppm, and a random end moment can be a Cenozoic-like low.
  Accept ~20% of ends below 180 ppm.
- C. A C3-starvation floor on the sink (Pagani et al. 2009: plant-assisted weathering falls as CO2 nears C3
  limitation). Today the model's weathering-weighted plant factor falls only ~10% at 100-130 ppm, because C4 and
  grass NPP keep it up. Check this against the literature before choosing.
Lean A with C checked. This changes the bar's variability (the deep-ice share and never-ice), so re-measure.

## Updates
- 2026-10-25: RULING (coordinator): A, with C checked. The drift should stand only for what the model lacks (organic burial, ocean chemistry). Its size comes from a literature number for non-degassing source variability, with the explicit outgassing's measured variance taken out, not from tuning the end pCO2. Check C (Pagani et al. 2009 plant-assisted weathering failing near C3 limitation) against the literature, and add it only if the mechanism is well supported and the model lacks it. Re-measure the PW-865 bar after both.
