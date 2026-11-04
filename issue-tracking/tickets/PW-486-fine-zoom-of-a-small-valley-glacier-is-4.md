---
id: PW-486
title: Fine zoom of a small valley glacier is 40% bigger than its parent's ice
type: task
status: todo
parent: PW-516
milestone: later
subsystem: zoom
effort: s
impact: low
found_by: pw392-fine-forms
blocked_by: []
relates: [PW-392, PW-127]
refs: [planet/zoom/fine_forms.py, "zoom de7be6 in e33c3d"]
created: 2026-10-20
updated: 2026-11-03
---

## Description
zoom_fine_forms.glaciers() runs zoom.glaciers() on the fine ground, with new ice allowed within a parent pixel (bilinear >= 0.1) of the parent's ice and the parent's inner ice kept. On e33c3d's small valley glaciers (de7be6, 50 km at 100 m) that is 244 km2 against the parent's 174 (171 before this change), IoU 0.71 (0.91), mean thickness 80 m, volume 19.6 vs 11.8 km3. On the ice sheets (7580bf in 225c65, cf5cdf in 39cf84) area and volume match the parent within 1% and 5% (volume 424 vs 422 and 630 vs 634 km3). The excess is fine crests and cirques, within a parent pixel of the ice, that the balance puts above the equilibrium line; the parent's 1 km mean smooths them away. It may be right (finer terrain, more summit ice) or the fine climate's lapse correction is too generous at the margin. To check against the regional zoom: build a regional zoom of the same place at 0.5 km and compare its ice area with the 1 km parent's and the fine one's. If the 0.5 km area is also larger than the 1 km area, the scale dependence is the glaciers' own (PW-127) and the fine zoom is consistent.
- [ ] ice area of the same valley at 1 km, 0.5 km and 0.1 km compared; cap ICE_NEAR if the fine zoom overshoots both

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: fine-zoom or coast-form polish; zooms read well enough
- 2026-10-20: Created from inbox draft draft-fine-zoom-glacier-margin-wider-than-parent.md (found by pw392-fine-forms).
- 2026-10-30: planet/zoom.py and planet/zoom_*.py moved into planet/zoom/ (regional.py, fine.py, ...) and zoom.build split into named stages (stage_*.py), lane 55; the file names here are the new ones, but the line numbers in the text are from before the move.
