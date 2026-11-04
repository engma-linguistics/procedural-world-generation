---
id: PW-572
title: "Two missing measurements: an overturning report (sites, Sv, heat, basin openness) and the thermostat's gain in ice_diag --summary"
type: task
status: todo
parent: null
milestone: later
subsystem: infra
effort: s
impact: med
found_by: base-climate-review
blocked_by: []
relates: [PW-458, PW-016, PW-558]
refs: [tools/climate_bias.py, tools/ice_diag.py, tools/earth_check.py, docs/review/base-climate-review.md]
created: 2026-10-22
updated: 2026-11-03
---

## Description
Stage 0 of the base-climate review.

**1. An overturning report.**
- Why: a rain-kernel change silently moved Earth's sinking from the Greenland Sea to Baffin Bay
  (draft-overturning-flipped-by-rain-kernel).
- Add an overturning section to earth_check (or climate_bias), so every climate change's check shows it. It should
  give:
  - the NH and SH sinking, in Sv;
  - each site's latitude and longitude;
  - the size of the basin each site sinks in;
  - the heat delivered, in PW.
- It should work on Earth and on any stored world.

**2. The thermostat's gain, as numbers in `ice_diag --summary`.**
- d ln(sink)/dT.
- The CO2 feedback in C per C (a regression after the spin-up).
- dT per C of drift.
- The sink split into land area, erosion supply, temperature factor and plant factor. This needs the Recorder to log
  the parts.
- The review's scratch scripts (`bc/thermo.py`, `thermo2.py`) did a rough version of this from the existing json.

- [ ] both print with one command each; a baseline row for main in `docs/review/base-climate-review.md`

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: tool or performance nicety
- 2026-10-22: Created from inbox draft draft-overturning-and-thermostat-reports.md (found by base-climate-review).
