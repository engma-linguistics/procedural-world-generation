---
id: PW-255
title: "Lakes and river routing: three settle passes and ~9 priority floods per step (~15% of an L7 run)"
type: task
status: done
parent: PW-247
milestone: v2
subsystem: hydrology
effort: m
impact: med
found_by: gpu-explore (PW-249)
blocked_by: []
relates: [PW-249]
refs: [planet/hydrology.py, planet/kernels.py, planet/surface.py, docs/review/gpu/profile.md]
created: 2026-10-15
updated: 2026-10-16
---

## Description
`surface.erode` -> `hydrology.lakes` runs `_settle` 3 times per step; each calls `_bed`
(`priority_flood` + `fill_shallow`), `kernels.lakes` (~2.6x per settle) and `hydrology.route`
(`priority_flood_to` + `accumulate_lakes`, ~2.9x per settle; 8.7 routes per step in all). All of
these are inherently sequential (heap order, union-find, topological order), so they don't
parallelise and won't go to a GPU. Per 100 Myr at 16 threads: ~5 s of an L6 run, ~26 s of an L7 run
(lakes 7.3, priority_flood 4.7, fill_shallow 2.8, route's priority_flood_to ~11).

Ideas, cheapest first: skip the 2nd/3rd settle pass when the lake set didn't change (early exit);
reuse the previous route's order when only lake levels moved; a single priority flood that also
returns the filled surface for `route`. Some change outputs slightly (check goldens / lake KPIs).
Expected 30-50% of this bucket.

## Updates
- 2026-10-16: Status in-progress -> done. Done (a0bbe6d, 5fe5fd9): stable radix sort, lake order reused per bed, flood_fill for _bed, Floyd heap pop; all outputs bit-identical (45 run files at L6 and L7). Lakes+routing L6 6.1 -> 3.4 s, L7 37.2 -> 23.6 s per 100 Myr; whole L7 run 180 -> 166 s.
- 2026-10-16: Bit-identical batch done on its branch (commit a0bbe6d): radix sort of the land cells in fill_shallow/lakes, lake order reused across _settle's tries, a filled-only flood (flood_fill) for _bed, Floyd's heap pop. Threadripper, 8 numba threads, load 12-18, seed 3199, 100 Myr: L6 lakes+route 6.1 -> 3.4 s (medians of 3 interleaved pairs; run 33.5 -> 30.9 s); L7 37.2 -> 23.6 s (one pair; run 180 -> 166 s). Every run file byte-identical (checkpoint, layers, run.json without id/timestamps). Early exits never fire on real inputs (L6, 10 sampled steps: _settle always takes all 3 passes, no try repeats the previous try's lakes, the final route's inputs never equal the last settle's), so none were added. What's left is priority_flood_to (route): ~60% of the bucket at L6, ~70% at L7, and ~40% of each flood (L7) is popping the sea's ~100k inner cells, which reach nothing but shape the heap and so the order of tied (flat lake surface) cells. Queuing only the outlets with a non-outlet neighbour makes the flood ~3.6x faster at L7 (22 -> 6 ms; would take the L7 bucket to roughly 10-12 s per 100 Myr) but changes down on ~0.6-2% of land cells (flow on ~1-3%; the filled surface is unchanged): needs new goldens and a look at lake/river KPIs. Not done (outputs change).
- 2026-10-16: Status todo -> in-progress. Agent started: bit-identical speedups only.
- 2026-10-15: Created from inbox draft draft-lakes-settle-passes.md (found by gpu-explore (PW-249)).
