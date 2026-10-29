---
id: PW-995
title: "Weathering has no land-area term: new low land adds almost no sink (supply-limited only). Keep it, or add a kinetic share?"
type: task
status: done
parent: null
milestone: v1
subsystem: climate
effort: s
impact: med
found_by: lane24
blocked_by: []
relates: [PW-980, PW-865]
refs: [planet/tectonics/earth.py, docs/review/base-climate/warm-drift/README.md]
created: 2026-10-29
updated: 2026-10-29
---

## Description
earth.weathering's sink is supply x climate x plants, and the supply is the erosion of bare, ice-free ground
(sim.weathered). The land share enters only through erosion, so low, flat new land adds almost nothing. In the
paired L6 set after PW-970, land is +3.5 to 4 points, yet the late erosion supply is 8% lower (ln -0.08). The sink did
not grow with the land, and the land's own effect on the finish is small and cooling: the true mean T is -0.25 C for
+3.5 points of land at fixed dT, from the climate's geography. This is why "more land should weather more" does not
happen in the model.

Options:
- A. Keep the purely supply-limited law. Flat, soil-mantled lowlands are supply-limited in the field: West et al.
  2005, the Amazon lowlands against the Andes (Gaillardet et al. 1999). GEOCARB's f_A (land area) is a global
  stand-in for the supply this model computes per cell.
- B. Add a kinetic share. Part of the sink would scale with ice-free land area x runoff x kinetics (West 2005's
  kinetic regime, and soil-mantled ground with a soil-residence floor), sized from the literature (~10-20% of today's
  flux off low-relief ground). More land would then weather a little more and cool.
- C. Use GEOCARB's f_A on the whole sink. This double-counts the supply, which already carries area.

Lean: A. The warm shift after the weld fix comes from erosion against the frozen reference (see the review note), not
from a missing area term. B is the physical option if the owner wants land area to cool.

## Updates
- 2026-10-29: Status needs-decision -> done. Coordinator 10-29 (geophysics delegated): keep weathering supply-limited for v1; low new land weathers little (a supply limit). Revisit a kinetic share with PW-470 in v2.
- 2026-10-29: Created from inbox draft draft-weathering-land-area-term.md (found by lane24).
