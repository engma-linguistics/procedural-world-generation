---
id: PW-1703
title: Seaward collapse (collapse_margin) gives back only a quarter of the Andean area loss; the area thermostat stays at its floor on L7 seeds 1 and 2
type: task
status: in-progress
parent: null
milestone: v1.0
subsystem: tectonics
effort: m
impact: high
found_by: lane 292
blocked_by: []
relates: [PW-1683, PW-1497]
refs: [docs/review/tectonics/l7-high-ground.md, docs/review/tectonics/mountains/l7_high_ground.py, "planet/tectonics/crust.py::margin_edges", "planet/tectonics/crust.py::margin_spread", "planet/tectonics/crust.py::flow_and_orogeny", "planet/tectonics/plate_kernels.py::crust_flow", "planet/tectonics/crust.py::thermostats", "planet/tectonics/crust.py::andean_contraction", "runs 213321 2e1bc2 28d710 6286ce (lane288 scratch, main 5411930b; to be deleted)", "runs 4635ef d4f6be eb41d6 a95c21 (lane292 scratch; to be deleted)", "Rey, Vanderhaeghe & Teyssier 2001 Tectonophysics 342:435", "Dewey 1988 Tectonics 7(6)", "planet/tectonics/params.py::collapse_margin_km", "runs ed0b66 285ffc 783fb3 5967e0 (lane296 scratch, deleted)"]
created: 2026-11-11
updated: 2026-11-11
---

## Description
In plain words: the new Andes take continental area away faster than the model's one area control can give it
back, so continents stand too high on some planets. Lane 292 built the fix lane 288 proposed: a dead mountain belt
at a coast also spreads out over the sea floor next to it, so the continent widens (parameter `collapse_margin`,
default off). It works, but it gives back only about a quarter to a third of the area the Andes take, and the
area control stays at its floor on both test planets. If nothing more is done, some December planets keep ~1.5-2x
Earth's share of land above 3 km and the area control has no slack left.

Numbers (l7-high-ground.md section 6, L7, medians 600-1000 Myr, against main 5411930b's on arms 213321 / 2e1bc2):
the thermostat stays at x0.20 on both seeds; mean continental crust 37.8 / 37.4 km (main 37.7 / 36.7); land above
3 km 4.96 / 3.45% (main 5.62 / 4.33%, off arms 3.90 / 2.77%, Earth on L7 2.5%); Andes share kept (23.5 / 20.4%).
Books at 1 Gyr: `collapse.margin` +9.2e3 against `andean.closed` -5.4e4 to -5.8e4 (km x L5 cells).

Why it is weak: `crust_flow` moves crust only where the thicker side is over 40 km, so seaward spreading stops once
the belt's edge is ~40 km; on Earth collapse runs on until the potential-energy contrast is gone.

Options:
- A. Seaward spreading of dead belts runs down to normal continental thickness (CONT_KM, 35 km) rather than 40 km,
  on the margin edges only. Physical in kind (Rey et al. 2001), but the reference thickness is a judgement and
  the rate has no source; one screen on L7 seeds 1-2.
- B. Make Andean closing give back the area it takes at the closing itself: the closed column's crust is stacked
  into a belt that is wider rather than taller (a distributed retro-arc fold-thrust belt advancing into the
  foreland, as the Andes' Subandean belt does). Changes PW-1497's belt shape; needs a source for the width.
- C. Accept the floor: the area holds near target (37.6-39.7%) and the high ground is within ~2x Earth on the
  worst seed; spend the time elsewhere.
Lean: A for one screen, then C if it does not get the thermostat off its floor.
- [ ] decision A, B or C

## Updates
- 2026-11-11: Lane 296 screened option A (`collapse_margin_km=35`, built default 40 = off; l7-high-ground.md sections 8-10): thermostat medians x0.20 / x0.21 on L7 seeds 1 / 2 (floor), give-back x1.5 (~0.43 of the closed area), area 39.3 / 40.2%, land > 3 km 3.92 / 3.30% against 4.96 / 3.45% on lane 292's arm rerun on the same commit. Fails the bar; option C written into the doc; decision C1/C2/C3 in a needs-decision draft.
- 2026-11-11: Status needs-decision -> in-progress. Coordinator: lane 296 screens option A (seaward spreading to 35 km), 2 seeds; if the thermostat stays on its floor, C (accept) and decide on the Andes default separately.
- 2026-11-11: Created from inbox draft draft-area-thermostat-floor-unsolved-after-collapse-margin.md (found by lane 292).
