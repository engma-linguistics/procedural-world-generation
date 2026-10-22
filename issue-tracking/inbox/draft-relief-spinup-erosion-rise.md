---
title: "The made-up start's relief takes 200-600 Myr to build up: the erosion supply rises ~3-4x and keeps creeping, which a kept CO2 reference turns into a long cooling"
type: task
status: todo
parent: PW-470
milestone: v2
subsystem: surface
effort: m
impact: med
found_by: base-climate-laneB2
blocked_by: []
relates: [PW-558, PW-576, PW-559]
refs: [planet/tectonics/setup.py, planet/tectonics/earth.py, docs/review/base-climate/thermostat.md]
---

## Description
Measured by base-climate lane B, stage 1 (the CO2 stock). The 10 L6 1 Gyr seeds (1 2 5 7 11 13 21 42 99 3199) are
in the session scratch `laneB2/`. Two 2 Gyr runs (seeds 5 and 13) are in `laneB2/g2/`.

- The ice-free land's mean erosion rate (`w_rate` in tectonics/diag) starts at ~5 m/Myr. It reaches 20-30 m/Myr
  only after 200 Myr (seed 1), 400-500 Myr (seeds 5 and 7) or ~600 Myr (seed 13). Over 2 Gyr it creeps up another
  ~+0.3 e-folds. The weathering supply rises ~e^1.0-1.4 over the run.
- The source is flat over the first ~1 Gyr, then rises ~+0.3-0.5 e-folds over 2 Gyr.
- Cause: setup.py starts the continents with low relief (cratons and old belts). Mountains have to be built by the
  first collisions.
- Cost:
  - With a CO2 reference kept from the end of the 300 Myr spin-up (PW-558/559 B), the still-rising supply draws
    CO2 down by 1-1.5 e-folds on seeds 5, 7 and 13. That gives 150-340 Myr deep eras (stage 1, attempt 1).
  - Stage 1 works around it with a relief term: the erosion rate of the ice-free land is measured against its own
    200 Myr mean (`earth.RELIEF_MYR`). That term also forgets part of real mountain-building's slow cooling, and part
    of the runoff's share of the brake.
- What I'd try: a start whose relief is already in balance with uplift, for example by pre-running the surface on
  the first geography, or by giving the old belts a settled relief. Then measure whether `w_rate` is flat from
  ~50 Myr. If it is, `RELIEF_MYR` could go, or get much longer.
- [ ] erosion rate within ~20% of its 300-1000 Myr mean by 100 Myr on 10 L6 seeds
- [ ] re-measure the thermostat (`tools/ice_diag.py --summary`) with and without the relief term
