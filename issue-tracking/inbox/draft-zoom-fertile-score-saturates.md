---
title: Zoom fertile_score is stored as a percent into a 0.01-scale byte, so it saturates at 2.55 (57% of section 2a4463's pixels)
type: task
status: todo
parent: PW-1198
milestone: v1.0
subsystem: zoom
effort: xs
impact: med
found_by: lane285
blocked_by: []
relates: [PW-1679, PW-099]
refs: [planet/humanuse.py::analyse_zoom, planet/humanuse.py::LAYER_SPECS, planet/export.py, planet/zoom/peoples.py, viewer/zoom.html, "zoom 2a4463", "zoom 44d6d6", tests/test_zoom_peoples.py]
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
