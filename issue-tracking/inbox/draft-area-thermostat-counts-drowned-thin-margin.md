---
title: The area thermostat counts thin drowned margin as continent, so keeping the margin costs 1.3 points of land
type: task
status: needs-decision
parent: null
subsystem: tectonics
effort: m
impact: med
found_by: lane-115
blocked_by: []
relates: [PW-1295, PW-970, PW-950, PW-046]
refs: [planet/tectonics/crust.py::thermostats, planet/tectonics/crust.py::coherence, planet/tectonics/crust.py::subduction_erosion, docs/review/tectonics/margin/pw1295-note.md, docs/review/tectonics/margin/diagnosis-land.md, docs/review/tectonics/margin/deep-dive.md, docs/review/tectonics/margin/paired_margin.sh, docs/review/base-climate/v1-finish-16/pjudge.py]
---

## Description
In plain words: PW-1295 now keeps margin cells of 15-20 km as continental crust instead of turning them into ocean
floor (that stopped them flickering). The thermostat that holds the continents' area at its target counts those thin,
deeply drowned cells as continent like any other. So it holds the same area (41%) with more drowned margin and less
thick crust: on the 36-draw judge the land is 1.3 points lower (33 of 36 draws), the continental crust 0.8 km
thinner, the drowned part 260 m deeper (scorecard: continental volume x0.97-0.98 of its target, from x1.00). Climate didn't move. The middle depths (200-3000 m) grew by 1.4 points,
towards Earth.

Why: on main the shreds of 15-20 km cells balanced the welds; now coherence is a net source of continental area
(screens, seeds 1 / 3: +11 000 / +12 500 km x cells per 400 Myr against -4 000 / -6 600), which the thermostat
answers with fewer births and more subduction erosion of thick crust.

Is the land change a problem? Earth is no target and 33% land is plausible, so this may be fine as is. If not, options:
- [ ] A: the area thermostat counts only crust at least BECOMES_CONT_KM thick (thin margin is the transition, not the
  continent's area). Note lane 100e's `pile_area` (drowned piles kept out of the area) was screened and didn't help, so
  screen first (seeds 1 and 3, tracediag.py)
- [ ] B: accept it (the margin is now kept, as on Earth's rifted margins)

Judge data: pw1295-note.md section 3 (scratch deleted; redo with paired_margin.sh from frozen copies of main before
and after PW-1295).
