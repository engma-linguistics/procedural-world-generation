---
id: PW-1052
title: An L7 run's spin-up ice sheets and vegetation on the L6 grid too (the coarse update is still half of an L7 one)
type: task
status: todo
parent: PW-247
milestone: later
subsystem: climate
effort: m
impact: med
found_by: lane27
blocked_by: []
relates: [PW-247, PW-252]
refs: [planet/nest.py, planet/tectonics/earth.py, docs/review/speed/README.md]
created: 2026-10-29
updated: 2026-11-03
---

## Description
**In plain words.** Before the last 10 Myr, an L7 run now works out its weather on the coarser L6 map, which is
about 5x cheaper. But the ice sheets and the plants are still worked out on the fine L7 map after each weather
update, and they now cost as much as the coarse weather itself. So one spin-up update costs about half of a full
L7 one, not a fifth. Moving them to L6 as well would make L7 runs faster still. The price is that the ice and the
plant cover, which carry over from one update to the next, would have to cross between the two maps.

Lane 27 profiled a steady-state L7 update on the L6 grid (seed 4242 at 120 Myr, cProfile, load ~60). It took
10.5 s: climate.compute on L6 4.5 s, the nest's restriction and prolongation ~1.0 s, ice_sheets on L7 2.9 s
(7 icemass.balance calls) and update_vegetation on L7 1.9 s. A native L7 update is ~21 s.

Options:
- Vegetation on L6. It is state: veg_frac and veg_lai are (NP, n) and warm-start the next update, and so are
  wv_frac, pot_frac and so on. Restrict them by area at each coarse update and prolong the results (masked, land
  only), then hand over at the finish window by prolonging. The ground cover, npp and npp_w that erosion and
  weathering read would come out as smoothed L6 fields.
- Ice on L6 is harder. The margins and the Nye profile are per cell, the glacial erosion and the T_ICE record
  read L7 ice, and the margin band is in km already (PW-725). Probably not worth it.
- The nest overhead (~1 s): `_prolong` runs per key in Python over ~60 fields. A single numba pass over a
  stacked field array would cut it to ~0.1 s. This is bit-for-bit only if the arithmetic order is kept.
- [ ] measure the vegetation-on-L6 variant's update time, and its NPP and tree-cover bias on one state
- [ ] judge it with the L7 set of docs/review/speed/README.md if it changes outputs

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: calibration or second-order physics refinement, not needed for the planet to be stable or for the culinary goal
- 2026-10-29: Created from inbox draft draft-l7-spinup-ice-and-plants-on-l6.md (found by lane27).
