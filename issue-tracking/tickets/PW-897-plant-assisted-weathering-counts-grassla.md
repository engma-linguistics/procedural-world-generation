---
id: PW-897
title: Plant-assisted weathering counts grassland like forest and feels no CO2 below 124 ppm, so it falls ~1.6x from 400 to 100 ppm where Beerling et al. 2012 find ~4x
type: task
status: todo
parent: PW-470
milestone: later
subsystem: climate
effort: m
impact: med
found_by: v1-finish-13
blocked_by: []
relates: [PW-865, PW-806]
refs: [planet/tectonics/earth.py, planet/vegetation.py, docs/review/base-climate/v1-finish-13/README.md]
created: 2026-10-26
updated: 2026-11-03
---

## Description
Check of option C on the drift ruling (Pagani et al. 2009: plant-assisted weathering weakens as CO2 nears C3
limitation, which floors CO2). Details in docs/review/base-climate/v1-finish-13/README.md section 3.

**The model already has the mechanism, so no separate floor was added.** Planted ground weathers through
GEOCARB's FERT, (2X / (1 + X))^0.4 (Volk 1987; Berner & Kothavala 2001). That term is GEOCARB's own form of this
feedback. On top of it, `plant_factor` follows the NPP, which falls with C3 photorespiration. A separate C3 floor
would count the same feedback twice.

**It is weaker than the literature.** From 400 to 100 ppm, against the balance's 500 ppm:
- FERT falls 0.954 -> 0.644, which is x0.675.
- The NPP part falls ~10% (v1-finish-12's measurement). C4 and grass NPP hold it up.
- Together the planted ground's weathering falls ~1.6x.
- Beerling et al. 2012 (J. Ecol. 100: 31-41; process model of roots, mycorrhizae and soil chemistry, late
  Miocene at 400, 280, 180 and 100 ppm) find the biosphere's weathering capacity falls about 4x over the same range.
- Quirk et al. 2014 (Biogeosciences 11: 321) measure a ~3x fall in tree-mycorrhizal Ca/Mg weathering from 1500 to
  200 ppm in growth chambers.
- Royer et al. 2014 (AJS, GEOCARBSULF error analysis) find that the plant weathering factors LIFE and GYM are
  2 of the 3 inputs that drive most of the CO2 uncertainty.

**Two pieces the model is missing:**
1. `plant_factor` counts NPP only. Grassland at 500 g C/m2/yr weathers like forest. Beerling's mechanisms 3-4 are
   the ECM -> AM shift and forest -> grassland, and they are part of the 4x. A tree/grass weathering factor (as in
   GEOCARB's GYM/angiosperm factor, field pairs of Moulton & Berner 1998) would add them.
2. `vegetation.CO2_RANGE` (1.5 doublings) holds the plants' CO2 responses at 124 ppm. Below that the plants (and
   so the weathering) feel no further starvation, although C3's compensation point is ~40-50 ppm. Ends at ~90-110
   ppm do occur (v1-finish-12 had 2/10, 583167 and 639472; this lane's shade set has 53669 c_p at 111).

Options:
- A. Add a tree-vs-grass factor to `plant_factor` (forest weathers more than grassland at the same NPP), sized from
  field pairs. Then lower the CO2_RANGE floor toward C3's compensation point. That second step makes the plants
  steeper, which the plants rule allows only where the literature supports it (it does here, Gerhart & Ward 2010).
- B. Leave it. FERT already gives a floor. The ends below 124 ppm are rare once the drift is sized
  (v1-finish-13), and the bar does not test end pCO2.
Lean B for v1 (rare after the drift fix; re-check in the v1-finish-13 tally) and A after v1. Either way it needs a
literature number for grass against forest weathering before any change.

## Updates
- 2026-11-03: Parked 11-03 per fresh-eyes review (docs/review/fresh-eyes/2026-11-03.md s3): milestone v2 -> later. Ice-age epic PW-470 is parked post-v1 (owner 10-28 timebox); PW-467 is the one kept as the timeboxed item.
- 2026-10-28: Status needs-decision -> todo. Coordinator 10-28: v2 under PW-470; not needed for the v1 bar.
- 2026-10-26: Created from inbox draft draft-plant-weathering-grass-as-forest.md (found by v1-finish-13).
