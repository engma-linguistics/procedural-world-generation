---
id: PW-147
title: Caprock strata are recorded as near-flat, so the zoom never makes cuestas
type: task
status: todo
parent: null
milestone: later
subsystem: surface
effort: m
impact: low
found_by: zoomland1
blocked_by: []
relates: [PW-010, PW-009, PW-649]
refs: [planet/landform.py, planet/zoom/landforms.py]
created: 2026-10-14
updated: 2026-10-26
---

## Description
The zoom turns dipping caprock into asymmetric cuestas (zoom_landforms
Caprock: the benches tilted by strata_dip along the regional downhill;
tested on a synthetic dip), but on world 800c99 (deleted) caprock cells' strata_dip is
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

## Updates
- 2026-10-26: Parent PW-005 (done) -> none. (PW-900 backlog reorg).
- 2026-10-23: Filed under the quality-pass epic PW-649 (relates PW-649, milestone later): shipped and judged good enough, residual kept for a later cleanup pass.
- 2026-10-14: Status needs-decision -> todo. Owner decision: B (record a broad regional tilt in the run so cuestas form), wanted for sure but low priority.
- 2026-10-14: Created from inbox draft draft-cuestas-need-dips.md (found by zoomland1).
- 2026-10-30: planet/zoom.py and planet/zoom_*.py moved into planet/zoom/ (regional.py, fine.py, ...) and zoom.build split into named stages (stage_*.py), lane 55; the file names here are the new ones, but the line numbers in the text are from before the move.
