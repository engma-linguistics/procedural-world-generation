---
id: PW-1080
title: The regional zoom's landscape stage still carries 13 closures (lake outlets, banks, falls, rerouting, routing, distributaries, the slope fit) defined inside one function
type: task
status: todo
parent: null
milestone: null
subsystem: zoom
effort: m
impact: low
found_by: refactor-lane-55
blocked_by: []
relates: []
refs: [planet/zoom/stage_landscape.py, planet/zoom/stage_rivers.py, planet/zoom/stage_terrain.py]
created: 2026-10-30
updated: 2026-10-30
---

## Description
In plain words. After splitting the zoom's build into named steps, the biggest leftover lump is the step called `drainage_tools` (about 660 lines): it defines a dozen helper functions (`lake_outlets`, `banks`, `rims`, `place_falls`, `reroute`, `route`, `make_branches` which is ~340 lines by itself, `fit_c`) as closures that read the build's shared state when called. They had to stay closures in the split because the landscape loop rebinds some of that state between calls (`active`, `outlet`, `land`, `sea`, the distributary lists), and the helpers must see the latest values. That keeps behaviour exact but means they still cannot be tested on their own.

Next step: turn each into a plain module-level function (or one small `Drainage` object) that takes what it uses as arguments, with the loop passing the current values. `make_branches` has nested helpers of its own (`curve`, `walk`, `toward`, `commit`, `grow`) that would become a small class. Check bit-for-bit output on regions with a delta, a lake and a river with falls, since the old late-binding is easy to break.
- [ ] each helper callable without a full build, with a small unit test (a toy raster with a lake, a fall, a delta)

## Updates
- 2026-10-30: Created from inbox draft draft-zoom-drainage-tools-out-of-closures.md (found by refactor-lane-55).
