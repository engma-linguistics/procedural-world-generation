---
id: PW-466
title: "Time zoom: show an icehouse era starting or ending (the run's dT trend across the window, at the step where the run's cycle switches on or off)"
type: task
status: todo
parent: null
subsystem: timezoom
effort: m
impact: low
found_by: pw462
blocked_by: []
relates: [PW-462, PW-104]
refs: [planet/timezoom/fields.py, planet/timezoom/sim.py, planet/tectonics/earth.py, docs/review/audit/ice-framing-deep-dive.md]
created: 2026-10-20
updated: 2026-10-20
---

## Description
PW-462 part 3: where the run's climate crosses into or out of an icehouse within or next to a step, a zoom
could show the era starting or ending. Today the zoom's global temperature is the run's dT at the moment,
constant over the window (`_Sim.dT_run`, `ClimateFields`), plus its own CO2/albedo/vegetation feedbacks.

What it takes:
- The window's base dT follows the run's own trend: interpolated between the keyframes either side of the
  moment (the run relaxes dT with a 5 Myr e-folding, `global_temperature`, so over a 1 Myr window it moves
  ~0.1-0.5 C in ordinary steps and up to ~1 C in a sharp transition). The full climate is refreshed every
  `climate_every` kyr already, so a moving base dT is a small change in `fields.py`.
- Where the transition is: the run's rule (draft-run-ice-cycle-mean.md) evaluated at a few dT between the
  two keyframes finds the dT where the cold-phase extent first exceeds the persistent extent (era start), and
  the window is centred on the time the trend reaches it.
- Honest limit: a 1 Myr window over a 4 Myr step shows an era's onset only if the run's dT crosses the
  threshold within it; the run's 5 Myr relaxation makes most onsets slow (Earth's own were ~0.3-0.5 Myr at
  the Eocene-Oligocene and ~0.5 Myr for the Northern Hemisphere at 2.7 Ma). Expect "the first glacials
  appear and deepen" rather than a switch. Lower priority than the window and the run's mean.
- [ ] base dT trend in the zoom; era_start / era_end offered by the phase picker (draft-tz-phase-picker.md)

## Updates
- 2026-10-20: Created from inbox draft draft-tz-era-start-end.md (found by pw462).
