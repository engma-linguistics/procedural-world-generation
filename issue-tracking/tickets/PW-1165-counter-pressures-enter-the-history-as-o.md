---
id: PW-1165
title: Counter-pressures enter the history as one cut to carrying capacity, from the life tables (war, plague, famine, predation)
type: task
status: todo
parent: PW-917
milestone: later
subsystem: peoples
effort: m
impact: high
found_by: lane-82
blocked_by: [PW-1148]
relates: [PW-917, PW-1147, PW-1148, PW-1068, PW-1108, PW-661]
refs: [docs/review/peoples-counterpressures/design.md, planet/lineages/history/model.py, planet/lineages/history/competition.py]
created: 2026-10-30
updated: 2026-11-03
---

## Description
In plain words: give war, plague, famine and dragon predation a single shared way to thin a people. Each one lowers how many people
a cell can hold for that people (its carrying capacity K). They do it by the share that its extra deaths cut from the people's growth
rate, or by the land it takes away. Each is reported per people as "share lost to war / plague / famine / predation".

Design: docs/review/peoples-counterpressures/design.md, "The shared plug".
- **Mixin.** A `CounterMixin` (history/counter.py) with `_counter_step(step, env, tags)` at the start of each step. It fills `_kept`
  (lines x cells); `_advance` multiplies K by it right after `_K`.
- **Formula.** `kept` = r' / r on lane 78's life table, where r' carries the stage hazards added (Euler-Lotka, `life_history.table`'s
  mortality override); land losses multiply directly.
- **Floor.** COUNTER_FLOOR = 0.05 (judgement: never species-ending).
- **Pulses.** Pulses keep a depletion field d per line and cell that recovers with e-folding RECOVER_YR / x (lane 78's growth multiple).
  During a pulse the depleted density also enters `invasion_weights`.
- **Epochs.** Deep: off. Glacial: equilibrium terms only. Recent: everything.
- **Output.** Per stored frame and per people: `lost.{war, plague, famine, predation}`, plus pulse events for settlements (PW-1108)
  and the brief.

- [ ] CounterMixin and the K multiplier, inert with every pressure at 0 (golden unchanged)
- [ ] lost.* in the run output and the workbench
- [ ] lane 77 suite reports lost.* and post-pulse cell flips

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: war, plague, events and life-history belong with the v3 civilization epic (PW-661); not needed for a first culinary brief
- 2026-10-30: Created from inbox draft draft-counterpressure-plug.md (found by lane-82).
