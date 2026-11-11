---
title: "LOD globe near the ground: the camera never tilts toward the horizon, and the line overlays float over the eased ground"
type: task
status: todo
parent: PW-1673
milestone: v1.0
subsystem: viewer
effort: m
impact: med
found_by: lane291
blocked_by: []
relates: [PW-1688, PW-1690, PW-415]
refs: [docs/review/zoom/lod-plan-v2.md, viewer/globe/dive.js, "viewer/globe/lodtiles.js::easeEx", "viewer/globe/lodtiles.js::groundRadius", viewer/globe/overlays.js, "viewer/globe/geometry.js::llPos", "viewer/globe/tabs.js::buildZoomOutlines", tools/viewer_lod_dive.py, "world dba204"]
---

## Description
**In plain words.** Scrolling down the globe now reaches ~1 km over the ground (PW-1688, lane 291), but the view stays
straight down like a map, and the river, border and zoom-outline lines hang in the air above the ground once you are
low. If this is never done, "down to the ground like Google Earth" looks like a flat map with stray lines over it: no
horizon, no mountains seen from the side.

What lane 291 left out of step 4 (plan section 4, "Camera"):
- **Tilt.** `dive.js` keeps OrbitControls' target at the planet's centre, so the camera always looks at the centre.
  The plan asks for a tilt toward the horizon below ~200 km that the user can tilt back. Needs the target moved to
  the ground point under the screen centre as the camera descends (continuously, so no jump), the orbit then turning
  about that point, and the tile choice (`updateLod`) using each tile's own distance (it already does) with the far
  plane out to the horizon (`scene.js::fitClip` already sets far to the horizon below r = 1.4).
- **Overlays at the ground.** Tiles and cells ease the height exaggeration to 1x between 2,000 km and 50 km
  (`lodtiles.js::easeEx`, the cells through a vertex-shader factor), but the overlays (`overlays.js`, `llPos`, the
  rivers' ribbons, settlements, the built-zoom outlines) are built at the globe's full exaggeration, so below ~500 km
  they float kilometres above the drawn ground. Either scale them with the same factor (a uniform, as the cells) or
  hide them below a height and let step 5's tile layers (the tile's own rivers) take over.
- [ ] below ~200 km the camera tilts toward the horizon as it descends, can be tilted back, and scrolling out returns
      to the straight-down orbit with no jump (tools/viewer_lod_dive.py, a turn per frame no larger than the dive's)
- [ ] at 20 km and 1 km over world dba204 the rivers and outlines lie on the ground (screenshot)
