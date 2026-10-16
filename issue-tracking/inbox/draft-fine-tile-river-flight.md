---
title: River flights through a fine tile follow the parent's course, high above it
type: task
status: todo
parent: null
subsystem: viewer
effort: s
impact: low
found_by: fine-zoom-3d
blocked_by: []
relates: [PW-129, PW-072]
refs: [viewer/zoom3d_fly.js, viewer/zoom3d.js]
---

## Description
"Fly along a river" works with fine tiles shown: the camera's ground comes from
groundY, which asks the finest tile, so the gorge and the fall's face appear at
the fine tile's resolution. But the course is still the parent's river pixels
(smoothed over 6 km), and the clearance is the parent's (500 + 500 m per km/px:
1 km above the water in a 1 km zoom), so inside a 50 m tile the camera flies
far above, and up to a parent pixel off, the fine river. Inside a fine tile,
follow its own river line (Tile.lines / rec) and drop the clearance to its
resolution, blending at the tile's edge.
