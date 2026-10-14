---
id: PW-166
title: World 800c99 lacks the new rift_strain and glaciated_myr layers; re-slice it for the demos
type: task
status: todo
parent: PW-005
subsystem: store
effort: s
impact: med
found_by: zoomland2
blocked_by: []
relates: [PW-011]
refs: [planet/landform.py, planet/zoom_landforms.py, "world 800c99", "run f59dd6", "zoom c34d7a"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
PW-011 added two landform layers from the record: `rift_strain` (ln beta of
the last rifting: the rift's fault-block throw) and `glaciated_myr` (Myr
since the cell was last under ice: a scoured, lake-dotted shield). Runs made
before keep neither in their keyframes (`world_from_frame` then raises and the
API replays), and sliced worlds made before lack them: the zoom falls back to
`zoom_landforms.DEFAULTS` (ln beta 0.4, never glaciated).

World 800c99 (the landform demo world) is such a world. Overwriting it was
refused by the permission classifier, so the demo zooms (e.g. rift c34d7a)
use the default 0.4; the record says 0.36 at that rift (fine) but 1.3-1.5 at
the coastal rift at (-18.56, 5.89). The verification runs injected the real
layers in memory (replayed from checkpoint 400 to 408).

Do: re-slice run f59dd6 at 408 Myr (`planet slice`; replays from t=0 unless
the code sha matches, ~15 min at L7) or rewrite 800c99 with the two layers,
then regenerate the landform demo zooms. Note: no shield on 800c99 was
glaciated in the last 80 Myr, so a scoured-shield demo needs another
(colder) run; tests/test_zoom_landforms.py has a synthetic one
(docs/review/landforms/zoom_shield_glaciated_synthetic.png).
- [ ] 800c99 (or its replacement) carries rift_strain and glaciated_myr
- [ ] landform demo zooms regenerated from it

## Updates
- 2026-10-14: Created from inbox draft draft-reslice-for-rift-strain-glaciated.md (found by zoomland2).
