---
id: PW-1337
title: "Land zoom memory: chunk the vegetation pass and find the 9 GB between live arrays and RSS"
type: task
status: todo
parent: PW-1299
milestone: later
subsystem: zoom
effort: m
impact: med
found_by: lane122
blocked_by: []
relates: [PW-1303]
refs: ["planet/zoom/vegetation.py::compute", "planet/zoom/stage_finish.py::vegetation_layers", "planet/zoom/landforms.py::Landforms", docs/review/land-zoom/cost.md, "world dba204", "zoom 69b422 (1 km, deleted)"]
created: 2026-11-02
updated: 2026-11-03
---

## Description
**In plain words.** After lane 122's fixes a 4000 km section at 1 km peaks at 86 GB (16 min), so two fit on the machine; the
goal of PW-1303 was several at once (~35-40 GB each). At 2 km the peak is in `vegetation_layers` (23.1 GB; its transient is
~8 GB over a 15 GB floor, many 0.4-1.8 GB arrays of 12 months or plant types over all pixels), and the floor itself is high:
RSS 15 GB at the end of the terrain stages against ~6 GB of arrays the build holds (landforms `lf` 2.7 GB; `fields` 0.8) and
10.6 GB live per tracemalloc; the rest is allocator/runtime overhead.
- [ ] run the vegetation and soils pass in pixel-row chunks (it is per pixel; check the few neighbour-using terms), same outputs (hash all layers)
- [ ] free `lf` (per-class `Ctx.w`, `prm`, 0.8 GB each) as soon as its last hook has run, and drop `fields` after `climate_on_terrain`
- [ ] try returning memory to the OS between stages (`malloc_trim`) and see how much of the 5 GB gap goes
- [ ] re-measure at 1 km with `/usr/bin/time -v`; target <= 40 GB
Harness: wrap the `stage_*` functions and sample `/proc/self/statm` (see cost.md).

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: zoom polish; zooms are good enough to read
- 2026-11-02: Created from inbox draft draft-land-zoom-memory-floor.md (found by lane122).
