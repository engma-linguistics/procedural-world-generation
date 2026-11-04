---
title: "Zoom detail grows with height, not relief: flat 4 km plateaus drawn as mountains and 9-10 km massifs on 8 km plateaus"
type: task
status: todo
parent: null
milestone: later
subsystem: zoom
effort: m
impact: med
found_by: scout-188-pw1446
blocked_by: []
relates: [PW-1446, PW-846]
refs: [docs/review/tectonics/mountains/scout2.md, docs/review/tectonics/mountains/scout2_land_amp.patch, docs/review/tectonics/mountains/scout2_subcell.py, docs/review/tectonics/mountains/scout2_peaks.py, docs/review/tectonics/mountains/scout2_earth_tail.py, docs/review/tectonics/mountains/scout2_trial.sh, docs/review/tectonics/mountains/pw846_fit.py, "planet/zoom/stage_terrain.py::detail", "planet/zoom/stage_terrain.py::coarse_fields", "planet/refine.py::terrain", "planet/zoom/stage_landscape.py::fit_setup", "planet/summit.py::sub_cell_relief", "planet/summit.py::local_relief", tests/test_zoom_landforms.py, tests/test_zoom_match.py, "world dba204", "zoom f4db12", "zoom fe600a", "zoom 3b412b", "zoom 0852e2", data/earth/raw_hydrosheds_dem_30s.zip]
---

## Description
In plain words: the zoom adds more rough detail the higher the ground is. On Earth, the detail inside a 60 km cell depends on how rugged the area around it is, not on its height. So the zooms turn flat high plateaus into mountains. On world dba204 they also build 40 km-wide massifs that average 9 to 10 km on top of an 8 km plateau, which is where the 12 km summits of zoom f4db12 come from (about half of PW-1446's overshoot). If this is never fixed, every zoom of high ground shows several km of relief that isn't in the world, and anyone reading a zoom's peak heights gets numbers about 1.5 to 2 km too high.

Measured by scout 188 (docs/review/tectonics/mountains/scout2.md §3-4), against Earth's HydroSHEDS 0.5-degree blocks at 4 km pixels:
- `amp_land = rug × (0.36 × base + 0.3 × step + 25) + 12` (stage_terrain.detail, refine.terrain). Flat cells (local relief under 300 m) at a 3.7-4.3 km mean get a p75 of 1.1-1.2 km above their mean, where Earth's is 0.13-0.3 km.
- Candidate patch on file, `scout2_land_amp.patch`: amplitude = rug × (summit.sub_cell_relief(local relief) / 1.5 + 25) + 12. On the same code and world, the highest pixel goes 11,456 → 9,890 m (zoom A, 61N 141W), 6,372 → 5,597 m and 5,470 → 4,668 m. Over the f4db12 view: 11,957 (stored) → 10,247 m. Each cell keeps its mean.
- With the patch, 3 tests fail that pass on main. `test_rift_has_fault_blocks_along_its_axis` compares against a zero-relief synthetic plain that is now (correctly) flat, so its comparison needs a ruling. `test_plunge_pool_lies_below_the_whole_fall` and `test_matched_section_carries_the_neighbours_rivers_on` need a look over re-rolled seeds.

- [ ] patch applied; the three tests settled (rift: a ruling on the comparison; the other two re-rolled over 3+ seeds)
- [ ] K = 1.5 checked on 2-3 zooms of a second world against the 4 km Earth table in scout2.md §3
- [ ] goldens updated if they move
