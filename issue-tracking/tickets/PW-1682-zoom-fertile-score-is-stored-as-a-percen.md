---
id: PW-1682
title: Zoom fertile_score is stored as a percent into a 0.01-scale byte, so it saturates at 2.55 (57% of section 2a4463's pixels)
type: task
status: done
parent: PW-1198
milestone: v1.0
subsystem: zoom
effort: xs
impact: med
found_by: lane285
blocked_by: []
relates: [PW-1679, PW-099]
refs: ["planet/humanuse.py::analyse_zoom", "planet/humanuse.py::LAYER_SPECS", planet/export.py, planet/zoom/peoples.py, viewer/zoom.html, "zoom 2a4463", "zoom 44d6d6", tests/test_zoom_peoples.py]
created: 2026-11-10
updated: 2026-11-10
---

## Description
**In plain words.** The farmland score behind the `fertile` classes is written as a whole percent (0 to 100) but the layer is
declared as a byte with scale 0.01, so the store divides by 0.01 again and clips at 255. In zoom 2a4463 (4,000 km section of world
dba204) 57.4% of all pixels read raw 255, which decodes as 2.55; the median, 90th and 99th percentile of the raw byte are all 255.
So the number the viewer shows ("score 2.55") and anything that reads it as 0 to 1 (peoples reads it as a percent and divides by
100, `peoples.py:144`) sees a flat ceiling, and the fertile classes (which are right: made before the encode) cannot be told apart
inside a class. Regional zooms and fine zooms (PW-1679 now writes it on rungs) share the path (`humanuse.analyse_zoom`,
`out["fertile_score"] = round(100 * score)`; worlds do the same at line 591 but their store spec may differ: check).

What breaks if never done: the fertile score is unusable as a number on every zoom, which the culinary end goal and the
settlement code both lean on. Fix: pick one convention (store 0..1 with scale 0.01, or declare scale 1 and keep percent), update
the readers that divide by 100 (export.py:717, peoples.py:144, viewer/zoom.html:1595 and viewer/globe/describe.js:225) and the
peoples test comment, and re-run `planet humanuse`-style recompute for existing zooms (old zooms may be deleted).
- [ ] decoded fertile_score spans 0 to 1 (or 0 to 100 by one stated convention) on a zoom, with no ceiling pile-up
- [ ] every reader agrees

## Fixed (lane 287, PW-1682)
`humanuse.world_layers` and `zoom_layers` now store `fertile_score` as a 0..1 fraction rounded to 0.01 (the store's encode
divides by the 0.01 scale; the world layer had the same bug, so the settlement site score read a 2.55 ceiling too). Readers that
divided by 100 (export.py, peoples.py, viewer/globe/describe.js) now read the fraction; viewer/zoom.html already showed it raw.
Tests: `test_no_zoom_layer_saturates_its_encoding` (tests/test_zoom_peoples.py, every scaled layer of a built zoom) and
`test_human_use_layers_fit_their_encoding` (tests/test_humanuse.py, world). No other saturating layer found. Zooms and worlds
made before this fix show a wrong fertile_score (clipped at 2.55); no code path was kept for them, delete or rebuild.

## Updates
- 2026-11-10: Created from inbox draft draft-zoom-fertile-score-saturates.md (found by lane285).
- 2026-11-10: Fixed by lane 287 (6e47b7fa), merged.
