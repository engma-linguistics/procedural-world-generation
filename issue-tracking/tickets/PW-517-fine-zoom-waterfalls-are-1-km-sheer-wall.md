---
id: PW-517
title: "Fine-zoom waterfalls are 1 km sheer walls: a 1186 m single drop, stretched texture on the face, staircased river above"
type: task
status: todo
parent: null
milestone: v1
subsystem: zoom
effort: m
impact: med
found_by: owner
blocked_by: []
relates: [PW-021, PW-375, PW-399, PW-516]
refs: [docs/review/screens/falls-1186m-a.png, docs/review/screens/falls-1186m-b.png, docs/review/screens/falls-1186m-c.png]
created: 2026-10-21
updated: 2026-10-21
---

## Description
Owner 2026-10-21, world 28442c, zoom 91486c (viewer ?world=28442c.json&tab=zoom&zoom=91486c): a fall marked 1186 m is a single vertical wall. The river ribbon hangs in the air as a straight line, the wall face shows stretched vertical streaks (texture stretched over a near-vertical triangle strip), and the river above comes down a pixel staircase. Real falls this tall are rare (Angel Falls 979 m) and mostly come as a gorge with a series of steps and cascades, the knickpoint having retreated into the plateau. Find where the drop comes from (designed falls in the zoom, the parent's relief refined into one cell, or a fine-zoom seam), then make tall drops read as a gorge plus a stepped cascade (cap a single step at a planet-relative height and split the rest into steps and steep rapids). In the viewer, steep faces should not show stretched streaks (triplanar or slope-based texturing) and the river line should follow the ground. Done when: no single fall above a few hundred m in the showcase fine zooms, and the 3D view of this spot looks like a gorge with falls rather than a wall.

## Updates
- 2026-10-21: Owner 2026-10-21 clarification: height is fine (even wild); the problem is form. Not a flat wide sheet dropping board-straight with terrain jutting up into a flat platform at the lip. Wanted: lip cut back into an amphitheatre/horseshoe (Niagara), plunge basin, irregular tiered face the water hits on the way down, a gorge below, surrounding slopes blending in. Done-when revised accordingly (no height cap).
- 2026-10-21: Created from the owner's screenshots (docs/review/screens/falls-1186m-*.png). Kept v1 because it looks broken at first glance; the rest of fine-zoom polish went to v2 epic PW-516.
- 2026-10-21: Created.
