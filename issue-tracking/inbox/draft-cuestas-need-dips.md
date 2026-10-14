---
title: Caprock strata are recorded as near-flat, so the zoom never makes cuestas
type: task
status: needs-decision
parent: PW-005
subsystem: surface
effort: m
impact: low
found_by: zoomland1
blocked_by: []
relates: [PW-010, PW-009]
refs: [planet/landform.py, planet/zoom_landforms.py, "world 800c99"]
---

## Description
The zoom turns dipping caprock into asymmetric cuestas (zoom_landforms
Caprock: the benches tilted by strata_dip along the regional downhill;
tested on a synthetic dip), but on world 800c99 caprock cells' strata_dip is
0.001-0.03 deg (median 0.006): flat strata get the regional slope of the
coarse land (landform.regional_dip), which is tiny at 55 km cells. Real
cuestas (Niagara ~0.3-0.5 deg, Paris Basin, Cotswolds) come from gentle
tilting the record doesn't keep (basin subsidence, flexure, broad uplift).
Options:
- **A.** Leave it: caprock is mesas and benches; cuestas appear only where a
  later batch (fold belts, PW-011) sets dips.
- **B.** Record a broad tilt for flat strata in the run: e.g. the change in
  the cell's elevation relative to its neighbours since the top stratum was
  laid down (tilting of a once-flat bed), as degrees.
- **C.** Let the zoom tilt caprock where the coarse land has a steady regional
  gradient over several cells (a basin margin), a few tenths of a degree.
Lean: A now, B if cuestas are wanted (it is physics, not a zoom fudge).
