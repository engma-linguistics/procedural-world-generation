---
id: PW-392
title: Fine zooms don't redraw glaciers, landform overlays, deltas or reef forms
type: task
status: todo
parent: null
subsystem: zoom
effort: m
impact: med
found_by: pw129-fine-zoom
blocked_by: []
relates: [PW-129]
refs: [planet/zoom_fine.py, "zoom a0097b", "zoom 652295"]
created: 2026-10-16
updated: 2026-10-16
---

## Description
Step 6 of docs/proposals/nested_fine_zoom.md is only partly built in
planet/zoom_fine.py:
- Glaciers: the parent's ice is used as is (bilinear mask, ice surface kept
  over the fine ground). Outlines and tongues aren't redrawn from
  icemass.balance on the fine valleys, as zoom.glaciers() does.
- Landform overlays (karst dolines, dunes, poljes) aren't drawn at the fine
  scale. The landform class is carried as is (nearest, warped).
- Coastal life and reefs come from the parent: coastal_life is nearest after
  a warp, and the reef terrain is the parent's elevation, bicubic. At 100 m
  from a 1 km parent, the reef rim's islets are rounded 1 km blobs (zoom
  a0097b, from 3ac681), and the reef patches have blocky, warped outlines.
- Deltas: the parent's distributaries are imposed only where they drain
  >= 25 parent px.

Each is a separate piece of work. The reef rim is the most visible. For a
reef or bay showcase I'd start with the reef forms (zoom_coastal.place at
the fine scale, kept to the parent's reef pixels).

## Updates
- 2026-10-16: Created from inbox draft draft-fine-zoom-not-redone-glaciers-landforms.md (found by pw129-fine-zoom).
