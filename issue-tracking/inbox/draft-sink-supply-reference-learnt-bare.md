---
title: The weathering sink's reference counts potential plants' weathering but bare ground's erosion; fix it together with PW-1158
type: task
status: todo
parent: null
milestone: v2
subsystem: climate
effort: m
impact: med
found_by: lane80
blocked_by: []
relates: [PW-1158, PW-1161, PW-980]
refs: [planet/tectonics/earth.py, docs/review/base-climate/finish-drift-l80/README.md]
---

## Description
In plain words. The model measures every world's carbon balance against a reference it learns in the run's first
300 Myr, before land plants exist. It already counts how much faster the rock would weather once plants grow. But it
does not count that plants also hold the soil, so the bare early land erodes up to 1.6x faster than planted land
later. As a result, the reference expects more weathering than a planted world delivers, and the finish comes out
about 1.6 C too warm. A second fault, the volcanic source sinking late in the run (PW-1158), makes it about 1.6 C
too cold. The two cancel, which is why the median finish sits near 0 C. They have to be fixed together.

Evidence (lane 80, lane 75's K judge, 18 L6 draws, scratch l80/plant.py, ts.py):
- When plants first appear (~505-530 Myr), the ln erosion rate steps down by a median of -0.27 (mean -0.21, 16 of 18
  draws negative). The ice-free area is flat (+0.00). The ln source over the same span is the control: -0.05. Relief
  adjusts afterwards, and the late supply sits at a median of -0.15 against the reference (850-1000 Myr).
- Cause: `erode()` has `k_mult = 1 + 0.6 wet (1 - veg)`. The spin-up has veg = 0. The sink reference in
  `global_temperature` uses `npp_pot` for its plant factor but takes the spin-up's own bare-ground `supply`.
- At the loop's gain (~11 C per e-fold), -0.15 is about +1.6 C. The source's late decline (median ln src +0.13 at
  300-350 Myr, -0.13 to -0.19 over 850-1000) is about -1.6 C. The median end T is +0.1 C.

Why fixing either alone is wrong: the supply fix alone moves the median about 1.5 C colder. That trades the warm
failures for cold and icy ones and risks the 100% frozen-over criterion. The source fix alone moves it about 1.5 C
warmer, so there are more warm failures (PW-1161). Together they are roughly neutral in the median and correct in
mechanism.

Fix sketch (behind a Params switch, no new constant): learn the reference supply at the potential vegetation's
ground cover. Scale each cell's spin-up supply by `(1 + 0.6 wet (1 - veg_pot)) / (1 + 0.6 wet (1 - veg))`. That is
the instantaneous ratio, which overstates the lasting step a little because relief re-grows (-0.27 at the step,
-0.15 late), so measure the outcome rather than assume it.
- [ ] Supply reference at potential cover, paired with PW-1158's source fix, on a screen; median end T within +-0.5 C of main
