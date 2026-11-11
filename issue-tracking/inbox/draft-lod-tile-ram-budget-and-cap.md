---
title: "LOD tiles: the tile service budgets 3.2 GB a tile, a build process peaks at 4.0-4.4 GB, and nothing caps one that runs away"
type: task
status: todo
parent: PW-1673
milestone: v1.0
subsystem: zoom
effort: s
impact: high
found_by: lane303
blocked_by: []
relates: [PW-1713, PW-1690, PW-1708]
refs: ["planet/api.py::TILE_PEAK_GB", "planet/api.py::tile_job", planet/tiles.py, "planet/zoom/lod_build.py::tile", "planet/zoom/lod_build.py::build_line_parents", "planet/zoom/fine_meander.py::_ease", docs/review/zoom/lod-plan-v2.md, "world dba204", "tiles py.1.1/4/7/151, py.1.1/4/7/163"]
---

## Description
**In plain words.** On 11-11 two tile builds of lane 303 grew to 102 GB and 37 GB in seconds and the kernel killed
them, taking the machine down. The cause was a bug on main (`fine_meander._ease` asked for a 23 GB array when a
river's meander phase stood still; fixed on lane 303, commit "Meander easing: cap its window"), but it showed two gaps
that would let the same thing happen on Daniel's server, where the tile service runs `lod_build.tile` in its pool:
1. **Nothing caps a build.** A bug of that kind in any one tile takes the whole machine, not just the job. A per-job
   memory cap (the pool's workers under `setrlimit(RLIMIT_AS)` or a cgroup, as `systemd-run --scope -p MemoryMax`)
   would fail that one tile with a MemoryError and its traceback instead.
2. **The budget is under the measured peak.** `api.TILE_PEAK_GB` gives levels 2-4 3.2 GB. Measured on dba204 with
   `/usr/bin/time -v`, `NUMBA_NUM_THREADS=4`, one process building tile after tile (lane 303, main's code with the fix
   and lane 303's branch): peak 4.22 GB (12 level-4 tiles plus a level-3 parent), 3.97 GB (9 level-4 tiles), 4.42 /
   4.34 GB (20 tiles of levels 2-4, branch). RSS after each tile creeps 1.9 -> 3.1-3.5 GB over the first ~10 tiles,
   then holds (caches: world, lru_caches, numba). A tile at a cell edge whose owner tiles aren't built builds them in
   the same process (`build_line_parents`, recursively: a level-4 tile can build level-3 and level-2 tiles of the
   neighbour); measured, that stayed inside the same 4.4 GB, but the job's budget doesn't count it.
If never done: the next runaway allocation in a tile build takes Daniel's machine down again, and the free-memory
check admits more concurrent tiles than fit.
- [ ] each tile job runs under a memory cap (a failed tile, not a dead machine), tested with a deliberate over-allocation
- [ ] TILE_PEAK_GB for levels 2-4 from the measured 4.0-4.4 GB peaks (and a recursive owner build counted, or queued)
