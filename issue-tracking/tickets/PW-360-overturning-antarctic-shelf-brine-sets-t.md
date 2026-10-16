---
id: PW-360
title: "Overturning: Antarctic shelf brine sets the North Atlantic's sinking threshold (Earth 15 -> 10 Sv with the shelves as sea)"
type: task
status: todo
parent: null
subsystem: ocean
effort: s
impact: med
found_by: pw354-earth-bed
blocked_by: []
relates: [PW-354]
refs: [planet/ocean.py, tools/earth_data.py, "docs/overview.md §2.7"]
created: 2026-10-16
updated: 2026-10-16
---

## Description
PW-354 made Earth's floating ice shelves (Ross, Ronne-Filchner, Amery; 92 L6 cells, ~0.3% of the
sea) sea instead of land. The L6 Earth's overturning then falls 16.9 -> 12.6 Sv, the north
14.9 -> 10.0 Sv, the south 1.9 -> 2.6 (observed AMOC ~17).

Diagnosis (L6 Earth, `ocean.overturning` instrumented):
- The cause is the deep-water reference. `ocean.overturning` takes one deep water per connected
  ocean, the densest 10% (by area) of its polar sea in *both* hemispheres, less moc_mix; water
  sinks only within moc_drho (0.3 kg/m3) of it. The new shelf seas grow brine-heavy ice and
  are the densest water there is: the south's share of that top 10% goes 19 -> 27% and the
  reference rises 1028.020 -> 1028.135 kg/m3. Through the spin-up's tightening gate the Nordic
  seas' marginal cells drop out, the inflow brings less salt and heat (N Atlantic >55N:
  SSS 35.30 -> 35.17, SST 4.0 -> 3.1 C) and the north settles on a weaker branch.
- It is bistable, not a normalisation. With the reference held fixed from the start, old and new
  geography give the same north (15.0 / 15.05 Sv at the new reference, SSS 35.285 / 35.282).
  So the salinity's S0 normalisation, the fresh-water books and the rain's global renormalisation
  contribute nothing measurable. Both 15 and ~11 Sv are steady states for the new geography,
  and the spin-up's path picks the weaker one.
- moc_iters = 4 isn't converged here: 8, 16 and 30 iterations give north 11.25-11.28 Sv (old
  data: 14.87, converged by 4).
- Per-hemisphere deep water (tried): Earth north 14.05 / south 2.48 Sv, insensitive to the
  shelves. But generated keyframes where one hemisphere's water outweighs the other's now sink
  in both: run 738c73 @652 18.1 -> 35.5 Sv, @300 21.5 -> 37.2. Other moments unchanged
  (46c0b2 @500 31.9, c32ec0 @700 41.4/41.8). Run goldens move (the run's climate uses it).

Options:
A. Keep it: AABW competing with NADW is the rule's intent, and Earth sits near the threshold.
   Accept 12.6 Sv (or ~13.8 converged) on the shelves-as-sea Earth.
B. Each hemisphere makes its own deep water (NADW forms over denser AABW on Earth). Robust on
   Earth, but doubles the overturning of one-sided generated worlds and lets any hemisphere's
   densest polar water sink.
C. Keep the shared deep water and fix the convergence (more iterations, or start the spin-up from
   the previous climate's state): no new physics, but it doesn't address which branch is right.
Lean: A plus C's convergence check (moc_iters 4 -> 8 costs ~+0.1 s per climate). B is a design
change for the ocean owner.

## Updates
- 2026-10-16: Status needs-decision -> todo. Coordinator 2026-10-16: A + C. Accept the drop as the shared-deep-water rule working (Antarctic shelf brine densifies deep water, the North Atlantic settles on its weaker state: AABW/NADW competition is real). Do C (the 4-iteration default isn't converged: north 11.3 Sv at 8+). B (per-hemisphere deep water) belongs with PW-016/PW-017's overturning work.
- 2026-10-16: Created from inbox draft draft-earth-overturning-shelves.md (found by pw354-earth-bed).
