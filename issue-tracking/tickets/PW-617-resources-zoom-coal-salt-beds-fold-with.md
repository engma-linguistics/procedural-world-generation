---
id: PW-617
title: "Resources: zoom coal/salt beds fold with the zoom's ridges by a proxy, not the fold-belt structure"
type: task
status: todo
parent: PW-155
milestone: v2
subsystem: zoom
effort: m
impact: low
found_by: resources2
blocked_by: []
relates: [PW-610, PW-649]
refs: [planet/zoom/resources.py, planet/zoom/landforms.py]
created: 2026-10-23
updated: 2026-10-23
---

## Description
zoom_resources.site() puts each coal or salt bed at the cell's column depth below a ~cell-wide mean of the
zoom's ground. In fold belts it adds 1.5 x the zoom's 10-20 km high-pass relief, so anticlines sit under
ridges, and oil and gas fields prefer that high-pass's crests. This is crude but cheap. The real structure
(each patch's strike, fold wavelength and dip) lives in zoom_landforms' FoldBelt/Ctx and is not stored on the
zoom. A better version would store the fold phase (or u, the distance across the strike) as a zoom layer when
the zoom is built, and fold the beds with it. The seams would then outcrop along the cuesta and fold scarps
the zoom draws, as in the design in docs/proposals/resources.md section 6. Flat-lying beds also have no
regional dip, so a bed outcrops only where valleys cut down to it.
- [ ] coal outcrop belts in a fold-belt zoom follow its ridges' strike

## Updates
- 2026-10-23: Filed under the quality-pass epic PW-649 (relates PW-649): shipped and judged good enough, residual kept for a later cleanup pass.
- 2026-10-23: Created from inbox draft draft-resources-zoom-bed-geometry.md (found by resources2).
- 2026-10-30: planet/zoom.py and planet/zoom_*.py moved into planet/zoom/ (regional.py, fine.py, ...) and zoom.build split into named stages (stage_*.py), lane 55; the file names here are the new ones, but the line numbers in the text are from before the move.
