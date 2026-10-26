---
title: Audit the run's per-step amounts for step-length dependence now that the finish window steps 0.5 Myr
type: task
status: todo
parent: PW-244
milestone: v1
subsystem: tectonics
effort: s
impact: med
found_by: v1-finish-16
blocked_by: []
relates: [PW-866]
refs: [planet/tectonics/simulation.py, planet/tectonics/earth.py]
---

## Description
PW-866 made the run's last `finish_window` (10) Myr step `finish_step` (0.5) Myr at a time (Simulation.step_length;
`sim.dt_now` is the step's length, `sim.dt` the run's 2 Myr step). Every `sim.dt` use in planet/tectonics was moved to
`dt_now`, which is right for rates times a step. But some quantities are amounts per step that feed a rate law
learnt at dt = 2:
- found and fixed (v1-finish-16): the carbon source's new-ocean-floor cells and plume melt, and the weathering
  supply (`sim.weathered`, km eroded in the last step). Unscaled, the 0.5 Myr steps cut source and sink to ~1/4
  while the arcs' term (a rate) stayed, warming the L4 300 Myr test worlds by several C at the end and flipping
  the forest-to-tundra multi-seed test from 16/17 to 0/2 eligible (re-rolled on seeds 1-72; back to 16/17 and
  18/18 after the fix).
- not checked: anything else that reads `sim.removed`, `newc`, the events' per-step counts, or a per-step
  probability without a dt (e.g. a chance per step). A quick audit: grep for per-step quantities feeding
  references or rates, and compare a run's last 10 Myr with finish_window=0 against the default for drift in
  sea level, CO2 and land share.
- [ ] audit done, any further per-step amount scaled to per-dt
