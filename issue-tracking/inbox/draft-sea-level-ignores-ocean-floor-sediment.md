---
title: Sea level ignores the water that sediment on the ocean floor displaces (about 125 m late in a main run)
type: task
status: needs-decision
parent: null
subsystem: tectonics
effort: m
impact: med
found_by: lane-100d
blocked_by: []
relates: [PW-950, PW-980, PW-1230]
refs: [planet/tectonics/earth.py, docs/review/tectonics/margin/diagnosis-land.md, docs/review/tectonics/margin/tracediag.py]
---

## Description
In plain words: when sediment piles up on the ocean floor, it should push the sea up, the way a stone dropped in a
glass raises the water. The model doesn't do this. Its sea level reads only how old (and so how deep) the ocean floor
is, plus the water standing over the continents. So the ocean slowly "loses" water as its floor fills with sediment.
Late in a main run that is worth roughly 125 m of sea level that never shows up.

Where: `earth.py` sea level. `sea_tect` comes from `ocean_depth(w_age)` over the oceanic crust only (the age-depth
curve, no sediment, no extra crust). `continent_water` counts the water over continental crust from `w_elev`, which
does include sediment. So sediment moved from a continental shelf to the ocean floor *lowers* the sea (the shelf
holds more water, and the floor's rise is not counted), when the sea should barely move.

Numbers (lane 100d, tracediag.py, L6 seeds 1 and 3, 600-1000 Myr means): the oceanic crust's sediment raises its
floor by a mean 181 / 186 m on main (22 m at 10 Myr). With 0.69 for the water's load on the floor (the factor
earth.py uses), that is ~125 m of missing sea level. With sea-floor creep at slope_k=1000 it is 292 / 252 m, and
`sea_cont` falls 24-42 m further, the wrong way.

Options:
- A. Count it: add the oceanic crust's sediment rise (from `isostasy.elevation` with and without the sediment) to the
  basins' part, against the start's value, as `continent_water` does for the continents. It's correct, but it lowers
  main's land (the sea rises ~100 m late, worth a few points of land) and re-sets calibration, so it needs a paired
  judge.
- B. Leave it, and document that sea level 0 is "the start's floor, with sediment uncounted".
Lean: A, judged on its own, because it conserves the ocean's water. Then retune nothing unless the soft pass drops.
- [ ] decision A or B
- [ ] if A: a test that moving sediment from a shelf to the ocean floor leaves the sea level unchanged within the
      isostatic difference
