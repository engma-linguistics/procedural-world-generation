---
id: PW-392
title: Fine zooms don't redraw glaciers, landform overlays, deltas or reef forms
type: task
status: done
parent: null
subsystem: zoom
effort: m
impact: med
found_by: pw129-fine-zoom
blocked_by: []
relates: [PW-129]
refs: [planet/zoom_fine.py, "zoom a0097b", "zoom 652295"]
created: 2026-10-16
updated: 2026-10-21
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
- 2026-10-21: Status todo -> done. Merged 374097d (2026-10-20, coordinator); follow-ups PW-485..489.
- 2026-10-20: Done in branch worktree-agent-aec8c3931c71791a9 (planet/zoom_fine_forms.py): glaciers via zoom.glaciers on the fine ground (parent ice kept; ice sheets 424 vs 422 km3 parent, was 409), karst/dune overlays via Landforms.finish (lineage seed `params.root_seed`, sub-parent-pixel part only; 7b0911 435 towers, db513c dunes 52 m), volcano reefs via zoom_volcanoes.fields and coastal life via zoom_coastal.place at the fine scale (a0097b: smooth bands, patches and an atoll ring; 327 km2 reef vs parent 535, 485 before). Deltas: the 25-px threshold isn't binding (all distributaries already carried in 5 parents); plain/coast forms filed as drafts, with parent coast steps, reef share, glacier margin and karst hatching. Measured in a scratch store; tests pass; goldens unchanged.
- 2026-10-16: Created from inbox draft draft-fine-zoom-not-redone-glaciers-landforms.md (found by pw129-fine-zoom).
