---
id: PW-552
title: "Zoom page: fine-zoom size menu is all disabled in 2-4 km zooms and can't target a shown fine zoom"
type: task
status: done
parent: null
milestone: v1
subsystem: viewer
effort: s
impact: med
found_by: owner
blocked_by: []
relates: []
refs: []
created: 2026-10-21
updated: 2026-10-21
---

## Description
Owner (2026-10-21), viewing fine zoom cd9e40 (100 km @ 200 m) inside zoom 106461 (2000 km @ 4 km): the size menu next to 'Fine zoom here' offers nothing finer. viewer/zoom.html fineSizes() builds its options from the page's zoom (106461, 4 km/px), and FINE_SIZES (50 km@100 m, 25@50 m, 25@25 m) are all more than MAX_STEP=20x finer than 4 km, so every option is disabled. Its 'default size' label (50 km @ 100 m) also disagrees with the server's default (zoom_fine default: res = max(0.1, parent/20) = 200 m, 100 km). Fix: build the options from the server's rules (sizes valid for this parent, matching the server default), and let 'Fine zoom here' on a shown fine zoom's tile nest in that fine zoom (so you can zoom into a zoom without opening it on its own page).

## Updates
- 2026-10-21: Status todo -> done. Size menu now comes from the server's rules (zoom_fine.size_options via GET /api/fine-rules?res_km=; test keeps menu == check()), default matches default_size (100 km @ 200 m in a 4 km zoom; 25 km @ 100 m in a 200 m zoom). 'Fine zoom here' nests in the finest shown fine zoom under the point (2D outlines, 3D tiles) that takes the size and has room, else a coarser one; the hint names it and the menu follows it. Fine zooms open on their own page with finer sizes. Verified in headless Chrome on world 91448a: made 0ca59d (in 9c8891, 2D) and f34db3 (in cd9e40, 3D). Screens docs/review/screens/pw552-*.png. Server restart needed for the new endpoint.
- 2026-10-21: Created.
