---
title: Viewer colour maths duplicated between palettes.js and ramps.js (sRGB, CIELAB, hex helpers)
type: task
status: todo
parent: null
subsystem: viewer
effort: xs
impact: low
found_by: viewer-lane-53
blocked_by: []
relates: [PW-1032, PW-1027]
refs: [viewer/globe/palettes.js, viewer/ramps.js]
---

## Description
In plain words. Two new viewer files each carry their own copy of the same colour arithmetic; one shared copy would be simpler.

viewer/globe/palettes.js (the peoples-colour previews, PW-1032) and viewer/ramps.js (the ramp previews, PW-1027) both define sRGB to CIELAB conversion and hex/RGB helpers. When the owner picks which previews become defaults, move the shared part into one module (ramps.js already sits where both the globe and the zoom can import it) and have palettes.js import it. Do this together with whichever of PW-1032 / PW-1027 lands first, so a dropped preview's code is deleted instead of refactored.
- [ ] one copy of lab/hex helpers, imported by both
