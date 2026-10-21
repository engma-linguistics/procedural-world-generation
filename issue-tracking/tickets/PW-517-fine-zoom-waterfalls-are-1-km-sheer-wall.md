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
- 2026-10-21: Diagnosis. Not a designed fall (stats.knickpoints is empty; the fall is `kind: drop`, 49 m3/s, under KP_MIN_Q 100), not a seam and not the parent's relief refined into one cell. The coarse river runs on a perfectly flat 1807 m surface (a closed basin of the volcanic-arc landform, ~25 km long, filled to its spill by the landscape pass) and spills over the rim into a valley whose floor is graded up from the sea (coast ramp 2 m/km): 259 m at 35 km inland. The river drops 1186 m in 3.4 km, 884 m of it in one 1 km link; the 5x5 plane fit on the face leaves a residual of 333 m, the walls rise 715 m above the lip within 3 km. Inbox: draft-drainage-flat-basin-spill.md.
- 2026-10-21: Owner changed the brief: tall is fine, the shape is the fault. New planet/zoom_falls.py (`carve`, run before the final drainage): a steep run (>= 7 deg links, >= 100 m x relief/6 km, >= 20 m3/s) keeps its drop but is redrawn as a gorge retreated into the plateau (12 km per km of drop x (Q/50)^0.25, at most 30 km), tiers of at most 300 m (scaled by the zoom's p99 relief over Earth's 6 km) with the lip's the biggest and each next 0.6x, rapids between, cone walls (29-48 deg, varying by tier and noise) cut from every bed pixel so nothing juts up round the lip, and a plunge basin (a lake pixel, 0.3x the tier, <= 60 m) under each tier. Viewer: steep faces blend the stretched map colour to greyed rock with triplanar noise; the fall ribbon rides the ground instead of the water level carried between lip and foot. Numbers (zoom 91486c, fall at -18.1, -150.15): largest single link 884 -> 265 m, links of >= 40 m 4 -> 13, plunge basins 0 -> 6 (to 60 m), face plane residual 333 -> 308 m at 104 vs 186 m/km, falls >= 500 m 1 -> 1 (589 m, listed over 3 px = lip tier + rapids). Zoom 911ad8 (Costa Rica): falls >= 300 m 3 -> 1 (three 1.2 km walls became a 629 m tiered one); f1815b has no steep-enough run (its 306 m fall is a gentle 54 m/km link, unchanged). At 1 km/px a tier is 1-2 pixels, so the horseshoe lip and the amphitheatre are only a funnel of the cone walls here; the rest needs the fine zoom (inbox draft-fall-carving-fine-zoom.md).

