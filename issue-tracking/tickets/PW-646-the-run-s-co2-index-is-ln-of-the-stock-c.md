---
id: PW-646
title: "The run's CO2 index is ln of the stock (co2_stock, 3 C per e-fold), but the plants read it as log2 (Ca = 350 x 2^co2): one of the two is wrong"
type: task
status: needs-decision
parent: PW-470
milestone: v1
subsystem: climate
effort: s
impact: med
found_by: base-climate-laneA22
blocked_by: []
relates: [PW-644, PW-558]
refs: [planet/tectonics/earth.py, planet/vegetation.py, planet/timezoom/plants.py, planet/timezoom/forcing.py]
created: 2026-10-23
updated: 2026-10-23
---

## Description
`tectonics/earth.co2_stock` keeps `sim.co2` as ln X, where X is the stock relative to its reference. `co2_term`
warms by `co2_sensitivity` (3 C) per e-fold. The time zoom's plants turn their CO2 term of dTg (C) into the same
index by dividing by `co2_sensitivity` (`Plants.co2_index`), so they count e-folds too.

`vegetation.potential` and `vegetation.envelope` say "the CO2 index is ~log2 of CO2 against today's". They build
Ci = 0.7 x 350 ppm x 2^co2. Since lane A22 (PW-644), CO2 sets every C3 plant's quantum yield and every plant's
water-use efficiency, so the unit now matters much more than it did.

Numbers (the runs in the store: index 5/50/95% = -1.33 / -0.31 / +0.98):
- log2 reading (as coded): Earth's zoom at its glacial maximum (co2 -1.04) has 0.49 x 350 = 170 ppm, near the
  LGM's 190. A run at -1.33 has 140 ppm.
- ln reading (consistent with co2_stock): 0.35 x 350 = 124 ppm at Earth's glacial maximum, and 92 ppm at -1.33.
  That is below where C3 plants can grow at all in hot months.

Also, 3 C per e-fold is ~2.1 C per doubling, below Earth's ~3. With Earth's sensitivity, the LGM's -3.1 C CO2 term
would be -0.72 e-folds (170 ppm).

Options:
- A: keep the plants' log2 reading. Document it as the plants' own scale: one index unit is a halving for the
  plants and an e-fold for the temperature. That is a fudge, but its Earth numbers are right.
- B: read the index as ln everywhere (Ca = 350 x e^co2). That is consistent, but it makes glacial and low-CO2 runs
  much harsher for C3 plants. If Earth's glacial CO2 should stay plausible, the zoom's `co2_share` or the run's
  `co2_sensitivity` would need revisiting.
- C: carry a real pCO2 (ppm) in the run, from the stock times a reference, and give it to the plants.
- Lean: C in the long run. For v1, A, and record it in the docstrings.
- [ ] A / B / C

## Updates
- 2026-10-23: Created from inbox draft draft-co2-index-units-ln-or-log2.md (found by base-climate-laneA22).
