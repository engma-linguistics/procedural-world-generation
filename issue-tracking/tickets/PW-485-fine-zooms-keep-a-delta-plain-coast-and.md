---
id: PW-485
title: Fine zooms keep a delta plain, coast and barriers as the parent drew them
type: task
status: todo
parent: PW-516
milestone: later
subsystem: zoom
effort: l
impact: low
found_by: pw392-fine-forms
blocked_by: []
relates: [PW-392, PW-129]
refs: [planet/zoom/fine.py, planet/zoom/regional.py, "zoom 38e327 in bdeca9"]
created: 2026-10-20
updated: 2026-11-03
---

## Description
PW-392 said a fine zoom imposes the parent's distributaries only where they drain >= 25 parent px. Measured: on five parents with deltas (bdeca9, dff894, 02734d, 3ac681, 634f6c) no parent river above 20 m3/s inside a delta plain lies below that threshold (zoom_fine's riv_all already carries all of them; a delta zoom 38e327 from bdeca9 has 208 km of rivers >= 10 m3/s against the parent's 147 km, the extra being meanders), so lowering it changes nothing, and that part of the ticket is closed as not binding.

What is still the parent's, interpolated, is the delta's own forms: the lobe and finger shape, prodelta, tidal flats, beach ridges and barriers (`zoom._deltas`, `_delta_forms`, delta_floor in zoom.build, interleaved with the drainage). At 100 m a finger or barrier a parent pixel wide is a 10-pixel blocky band. Redrawing needs those forms factored out of zoom.build (they use the Galloway weights in the parent's stats["deltas"]) and drawn on the fine pixels, kept to the parent's coast like the reefs.
- [ ] fine delta lobes, barriers and tidal flats drawn from the parent's delta record at the fine scale, parent pixel means kept

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: fine-zoom or coast-form polish; zooms read well enough
- 2026-10-20: Created from inbox draft draft-fine-zoom-delta-plain-not-redrawn.md (found by pw392-fine-forms).
- 2026-10-30: planet/zoom.py and planet/zoom_*.py moved into planet/zoom/ (regional.py, fine.py, ...) and zoom.build split into named stages (stage_*.py), lane 55; the file names here are the new ones, but the line numbers in the text are from before the move.
