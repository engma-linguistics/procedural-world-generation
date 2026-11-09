---
id: PW-1509
title: Andes-type ranges need the overriding plate to contract; no thermostat-friendly shortcut exists
type: task
status: wontdo
parent: null
milestone: later
subsystem: tectonics
effort: l
impact: med
found_by: scout 209
blocked_by: []
relates: [PW-1293, PW-1446, PW-846]
refs: [docs/review/tectonics/mountains/scout6.md, docs/review/tectonics/mountains/scout6_andean.patch, docs/review/tectonics/mountains/scout6_measure.py, docs/review/tectonics/mountains/scout6_screen.sh, docs/review/tectonics/mountains/scout1.md, "planet/tectonics/crust.py::arc_growth", "planet/tectonics/crust.py::thermostats", "planet/tectonics/crust.py::stack_collisions", "planet/tectonics/crust.py::subduction_erosion", "planet/tectonics/plate_kernels.py::resolve", "Medvedev et al. 2006 (The Andes, ch. 23)", "Gotberg, McQuarrie & Carlotto 2010 GSA Bull 122", "Schellart 2008 GSA Bull 120"]
created: 2026-11-08
updated: 2026-11-09
---

## Description
In plain words: on Earth a quarter of the land above 3 km is the central Andes, built mostly by squeezing the edge of
South America as it rides west over the Nazca slab. The model has no such squeezing, so its high ground is almost all
collision plateau (scout1: 8-10% near ocean-continent margins; scout 209 measured 11-18% on main, 3 L6 seeds x 600 Myr).
If never done, the worlds keep showing few coastal cordilleras (no Andes, no Rockies-type margins), so rain shadows,
coastal deserts and high-altitude peoples are rarer than on Earth.

Scout 209 (pass 1 of 3 on PW-1497, the coordinator's ticket for this) screened overriding-plate shortening at the
sourced rate (a third to all of the plate's trenchward advance, ~1 cm/yr; Medvedev et al. 2006, Gotberg et al. 2010,
Schellart 2008), with five ways of paying for the stacked crust. All failed on the same point: Andean shortening moves
~7x more crust per km of trench than the arcs, and on rigid plates on a fixed grid the area the plate loses can't be
represented. New volume overshoots the volume thermostat (+15-25% volume; land above 3 km 5-12% against main's
1.4-2.7%, baseline main on the same seeds); taking it from the whole plate drowns the interior (land 34% -> 24%);
taking it from the trench edge collapses continental area (40% -> 27-31%). Numbers: scout6.md.

Options:
- A. A lane (effort l) makes the overriding plate contract: its cells near an advancing ocean-continent trench close
  up toward the trench at the shortening rate (plate-frame strain in plates/plate_kernels.resolve, like a
  collision's overlap), so volume is kept and area is lost the way Earth loses it; then a margin belt with its own
  narrow spread behind the arc. Judge as scout1 section 6 says (Andes share + total high ground + two-tier bar).
- B. Accept that high ground is mostly collisional and close PW-1497 as a known Earth difference (documented in
  overview.md section 7).
- C. A cheaper partial: let the continental arcs' volume thermostat go to zero (no 0.1 floor) and route only that
  freed budget into a narrow margin belt. Not screened in that form (the budget arm only removed the cap above 1);
  it still concentrates volume, so total high ground likely rises.

Lean: B for now (stable, not fiddly), A as a later physics side-track item if margin ranges matter to the culinary or
peoples work.

## Updates
- 2026-11-09: Option B confirmed by PW-1497's third strike (scout 240, docs/review/tectonics/mountains/scout8.md): option A (real contraction, scout7.md) works at the present Andes rate only by making 4-8x main's high ground, and at the long-term rate does not raise the margin share. Documented in overview.md section 7 (Andean margin).
- 2026-11-08: Status needs-decision -> wontdo. Coordinator 11-08 (owner defers geophysics calls): option B for now. High ground stays mostly collisional, a known Earth difference. Option A (overriding plate truly contracts near an advancing trench, effort l) is the next attempt on the physics side track, tracked on PW-1497.
- 2026-11-08: Created from inbox draft draft-andean-shortening-needs-plate-contraction.md (found by scout 209).
