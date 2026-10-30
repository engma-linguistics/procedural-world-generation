---
id: PW-1078
title: "Time zoom: the ice surface's own summer damping still counts the sheet's air twice"
type: task
status: todo
parent: PW-470
milestone: null
subsystem: timezoom
effort: s
impact: low
found_by: lane28
blocked_by: []
relates: [PW-1050, PW-336, PW-555]
refs: [planet/timezoom/sim.py, planet/icemass.py, docs/review/base-climate/ice-loop/README.md]
created: 2026-10-30
updated: 2026-10-30
---

## Description
In plain words. An ice sheet chills the summer air in two ways in the model. Its own cold air mass spreads
over and around it (the "carried air"). And each ice cell's bright surface damps the summer of whatever air
sits on it. For the share of the air that already is the sheet's own air, the second effect takes the
summer's warmth off a second time. PW-1050's fix (a) makes the surface damp only the rest of the air:
icemass.sheet_cover(grid, ice, air) = LOCAL x (1 - air). That now holds in the run, the worlds' climate and the
zoom.

The time zoom's own ice kernel (timezoom/sim.py: `self.damp`, and the frames' `sheet_cover(g, np.ones(n))`)
still damps all of its air with LOCAL, while its climate (timezoom/fields.py, climate.compute with ice_air)
carries the sheet's air too. So the time zoom's sheets get the double count the run no longer has.

Fix: pass `air=icemass.sheet_air(g, H)` (the time zoom's ice) to its sheet_cover calls. The time zoom's own
surface_share (PW-555 stage 1) scales a different effect and stays. It is parked with the rest of the
ice-age physics (PW-470).
- [ ] The time zoom's surface damping uses LOCAL x (1 - sheet_air) like the run
- [ ] The time zoom tests and goldens updated

## Updates
- 2026-10-30: Created from inbox draft draft-timezoom-surface-damping-on-sheet-air.md (found by lane28).
