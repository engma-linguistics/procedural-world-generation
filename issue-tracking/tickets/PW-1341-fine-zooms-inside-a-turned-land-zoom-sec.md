---
id: PW-1341
title: "Fine zooms inside a turned land-zoom section: 2D boxes drawn unturned, fine zoom stays north-up"
type: task
status: todo
parent: PW-1299
milestone: v2
subsystem: viewer
effort: s
impact: low
found_by: lane127
blocked_by: []
relates: [PW-1338, PW-129]
refs: ["viewer/zoom.html::drawFine", "viewer/zoom.html::fineHost", "viewer/zoom3d_place.js::place", "planet/zoom/fine.py::zoom", "planet/zoom/regional.py::frame_of"]
created: 2026-11-02
updated: 2026-11-02
---

## Description
**In plain words.** A regional zoom can now be turned (PW-1338: `--section`, `--up`). A fine zoom (25-100 m/px) made
inside it is still north-up (`fine.zoom` builds `Frame(lat, lon)`); its parent frame is read correctly
(`regional.frame_of`), and the 3D view places it by a fitted affine map, so it lands in the right place turned. But
the 2D map draws each fine zoom's outline as an axis-aligned square at its centre (`drawFine`'s `box`), and the pick
square while arming is axis-aligned too: in a turned section both are drawn unturned (wrong by the section's bearing,
up to 45 degrees or more near the poles). Either draw the fine zoom's true corners (`aeFrame(...).toSphere` of its four
corners into the page's plane), or build fine zooms in their parent's orientation (`up` = the parent's up).
- [ ] a fine zoom's outline in a turned section's 2D map matches where its 3D tile lands

## Updates
- 2026-11-02: Created from inbox draft draft-fine-zoom-in-turned-section.md (found by lane127).
