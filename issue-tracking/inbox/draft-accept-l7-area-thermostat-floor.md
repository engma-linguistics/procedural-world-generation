---
title: With the Andes on, the L7 area thermostat stays at its floor after both give-back attempts; accept it, turn the Andes off at L7, or make belts wider
type: task
status: needs-decision
parent: null
milestone: v1.0
subsystem: tectonics
effort: s
impact: high
found_by: lane 296
blocked_by: []
relates: [PW-1703, PW-1693, PW-1497, PW-1683]
refs: [docs/review/tectonics/l7-high-ground.md, docs/review/tectonics/mountains/l7_high_ground.py, docs/review/tectonics/mountains/area_books.py, "planet/tectonics/crust.py::thermostats", "planet/tectonics/crust.py::andean_contraction", "planet/tectonics/crust.py::flow_and_orogeny", "planet/tectonics/crust.py::margin_edges", "planet/tectonics/crust.py::margin_spread", "planet/tectonics/plate_kernels.py::crust_flow", "planet/tectonics/params.py::collapse_margin_km", "runs ed0b66 285ffc 783fb3 5967e0 (lane296 scratch, deleted)", "Rey, Vanderhaeghe & Teyssier 2001 Tectonophysics 342:435"]
---

## Description
In plain words: the new Andes take continental area away faster than the model's area control can give it back.
Two lanes tried to give the area back by letting dead mountain belts at a coast spread out over the sea floor
(lane 292: spreading stops at 40 km crust; lane 296: lets it run down to normal 35 km crust). Each helped a little,
neither freed the area control, which stays at its lowest setting on both test planets. So on some planets the
continents stay a little too thick and too high. Two attempts have failed; a third would put this at the back of
the line. Daniel decides what to do with what is left.

Numbers (l7-high-ground.md sections 9-10; L7, medians 600-1000 Myr; baseline is lane 292's arm rerun on the
same commit, `collapse_margin=1` with the 40 km stop):
- lane 296's option A (`collapse_margin_km=35`): area thermostat x0.20 / x0.21 (floor 0.20) on seeds 1 / 2, against
  0.20 / 0.20; area 39.3 / 40.2% (target 40) against 38.5 / 38.2%; continents 37.2 / 36.0 km against 37.8 / 37.4;
  land above 3 km 3.92 / 3.30% against 4.96 / 3.45% (Earth on the L7 grid 2.5%; main with the Andes on and no
  collapse_margin 5.62 / 4.33%, Andes off 3.90 / 2.77%). Give-back rose from ~0.30 to ~0.43 of the area Andean
  closing takes. Two seeds cannot tell the high-ground fall from run history.
- Both parameters stay off (`collapse_margin` 0, `collapse_margin_km` 40).

What C (accept) means: with `andean_shortening` on, some L7 planets keep land above 3 km at ~4-5.6% (about 1.7-2.2x
Earth on the same grid), above 4 km up to ~3.4% (Earth 1.6%), continents ~1-2.5 km thicker than without the Andes,
and the area thermostat has no slack for any further area sink.

Options:
- C1. Accept it. The area holds near target, seed 2 is a plausible high planet, seed 1 is the worst case. Keep
  `collapse_margin` and `collapse_margin_km` as off switches; a later physics lane can revisit after v1.0.
- C2. Turn `andean_shortening` off at L7 only. Restores the no-Andes numbers (2.8-3.9% above 3 km) but showcases
  (L7) lose the Andes belts that L6 has, and L6 and L7 runs of one seed stop being the same model.
- C3. Andean belts wider instead of taller (lane 292's option B: the closed column becomes a broad retro-arc fold
  belt advancing into the foreland, like the Subandean belt, so closing takes less area in the first place). The
  most physical fix, but it is a third mechanism (three-strikes rule), changes PW-1497's belt shape, and needs a
  source for the width.

Lean: C1. Earth is a plausibility anchor, not a target, and 1.7-2.2x Earth's 3 km tail on the worst seed is a high
planet, not a broken one; C2 trades a visible feature for a hypsometry number and splits the levels; C3 is a
sound idea but belongs after v1.0 behind the three-strikes queue. A cheap variant of C1 for the coordinator: run
the 18-draw judge once with `collapse_margin=1 collapse_margin_km=35` to see whether it is worth turning on for its
smaller wins (area on target on seed 2, thinner continents, slightly wider shelves), knowing it does not free the
thermostat.
- [ ] decision C1, C2 or C3
