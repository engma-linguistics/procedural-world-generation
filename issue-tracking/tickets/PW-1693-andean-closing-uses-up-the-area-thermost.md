---
id: PW-1693
title: Andean closing uses up the area thermostat's only lever; on L7 seeds 1 and 2 continents end 1.4-2.5 km thicker and land above 3-4 km up to 2x Earth
type: task
status: todo
parent: null
milestone: v1.0
subsystem: tectonics
effort: m
impact: high
found_by: lane 288
blocked_by: []
relates: [PW-1683, PW-1497, PW-1680, PW-046]
refs: [docs/review/tectonics/l7-high-ground.md, docs/review/tectonics/andes-late.md, docs/review/tectonics/mountains/area_books.py, docs/review/tectonics/mountains/l7_high_ground.py, "planet/tectonics/crust.py::thermostats", "planet/tectonics/crust.py::andean_contraction", "planet/tectonics/crust.py::subduction_erosion", "planet/tectonics/crust.py::flow_and_orogeny", "planet/tectonics/crust.py::coherence", "runs 2e1bc2 6286ce 213321 28d710 (scratch lane288, kept)", "Dewey 1988 (extensional collapse of orogens)"]
created: 2026-11-10
updated: 2026-11-11
---

## Description
In plain words: the model keeps the continents' area near 40% of the surface with one control, how fast trenches
grind continents away (subduction erosion), and that control can only slow to a fifth of its normal rate. The new
Andes (PW-1497) remove about as much continental area as that control can give back (1.8-2.1% of the surface per
100 Myr, lane 288's area books). On runs where area also runs short for other reasons, the control sits at its
floor for hundreds of Myr; the area just holds its target but the same crust volume is spread over less of it, so
the continents stand ~1.2-1.5 km thicker and ~200-250 m higher everywhere. On L7 seed 2 that is the whole
difference between 2.8% of land above 3 km (as Earth's 2.5%) and 4.3% (lane 288, l7-high-ground.md 2.2); on L7
seed 1 the control is at its floor from ~100 Myr, area ends 2.4 points under target, and land above 3 / 4 km is
5.6% / 3.4% against 3.9% / 1.1% without the Andes (Earth on the L7 grid 2.5% / 1.6%; 2.4). It hit the floor on
2 of 2 L7 seeds and 1 of 3 L6 seeds (lane 286).

If never done: some showcase planets have broad 3-4 km uplands ~1.6x as often as Earth (land above 4 km stays
Earth-like), and the area thermostat has no slack left for any further area sink.

What to try, in order of soundness (not built; each needs a screen and then the 18-draw paired judge):
- A. Collapse that gives area back: a thick dead belt at a continent's edge spreads outward as well as inward
  (Basin and Range roughly doubled its width), so lower-crustal flow from a dead belt may also cross into the
  same plate's neighbouring ocean cell, which becomes continent when it reaches the birth thickness. A negative
  feedback on thickness itself, not on a global target; closes the loop shortening opened.
- B. Andean closing steered by the area thermostat (`andean_steer`): built, rejected by lane 286 (no consistent
  sign over two seeds, weaker Andes).
- C. A lower floor for subduction erosion (x0.2 -> x0.05): a clamp move, not a mechanism; listed only to reject.
- [ ] A built and screened on L7 seed 2 (on arm 2e1bc2's numbers: > 3 km median 600-1000 4.33%, thermostat x0.20)
- [ ] the paired judge, 0 hard failures, before any default change

## Updates
- 2026-11-11: Lane 292 merged: collapse_margin and water_loaded built, both off; neither lifts the floor. Continues in PW-1703.
- 2026-11-10: Created from inbox draft draft-andean-area-sink-exhausts-thermostat.md (found by lane 288).
