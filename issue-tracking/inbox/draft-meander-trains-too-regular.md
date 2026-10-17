---
title: Fine zoom meander trains are perfectly regular at full swing
type: task
status: todo
parent: null
subsystem: zoom
effort: s
impact: med
found_by: pw412
blocked_by: []
relates: [PW-405, PW-412, PW-416, PW-094]
refs: [planet/zoom_fine.py, _courses, _river_phase, "zoom 352c76 (scratch regen, 3453b8 -> 25 m)"]
---

## Description
With floors (PW-412), alluvial reaches now get their full meander swing (MEANDER_OMEGA 1.2 rad). The sine-generated trains are identical bend after bend: the same wavelength (11 widths) and the same swing all along a reach. In plan view they read as a drawn wave, not a river (e.g. 352c76, the 310 m^3/s river). Real trains vary: wavelengths scatter about ±30% around ~11 w, and bends are skewed and of uneven size.

Suggested fix (planet-fixed, so sibling zooms agree):
- In `_river_phase`, scale each node's phase increment by (1 + ~0.3 n), with n a planet-fixed fbm at the node.
- In `_courses`, scale the swing (om) by a smooth planet-fixed noise (about ±0.2 rad over a few wavelengths), still capped by the room.
- Optionally add a skew (Kinoshita third harmonic).

Keep the PW-405 test's 8-16 w mean wavelength.

PW-416 (migration over time) would make trains irregular anyway. This ticket is for the static fine zoom.
