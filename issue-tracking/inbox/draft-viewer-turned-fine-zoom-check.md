---
title: Viewer: check that fine zooms built in a turned parent's orientation draw right in 2D and 3D, then close the viewer half of the turned-section fine zoom ticket
type: task
status: todo
parent: PW-1299
milestone: v1.0
subsystem: viewer
effort: s
impact: med
found_by: lane283
blocked_by: []
relates: [PW-1341, PW-1674, PW-1198]
refs: ["viewer/zoom.html::drawFine", "viewer/zoom.html::fineHost", "viewer/zoom3d_place.js::place", "planet/zoom/fine.py::zoom", "planet/zoom/regional.py::frame_of", "tests/test_zoom_fine.py::test_fine_zoom_keeps_a_turned_parents_orientation"]
---

## Description
**In plain words.** PW-1674 now builds a fine zoom with the same orientation as its parent (`center.up` is the parent's,
`zoom.json` has `projection.up_bearing_deg`). For a north-up parent nothing changes. For a tiling section (turned by up
to 45 degrees or more near the poles) the fine zoom is now turned the same way, so its pixels line up with the
parent's. The generation half of PW-1341 is done (a real build was made: section px.1.1 of world dba204 at 4 km, then a fine
zoom of it, whose `center.up` is the parent's). Not done: the viewer. `drawFine` (the 2D outline of each fine zoom, and the
pick square while arming) draws an axis-aligned square at the fine zoom's centre in the page's plane; with the child now
turned like the page's own plane that should be right, but it was never checked on a section that is really turned
(faces pz/mz, or any cell near a pole; px.1.1 has up = north), and a fine zoom made BEFORE this change in a turned
parent is still north-up (delete and remake those). Also check the 3D placement (`place`, a fitted affine map) and the
Fine zooms list's fly-to for turned children, and a fine zoom of a fine zoom in a turned section.
- [ ] a turned section (e.g. pz.1.1 of a showcase world at 4 km) with a fine zoom and a fine of that: outline in 2D matches where the 3D tile lands
- [ ] PW-1341 closed or its remaining text updated
