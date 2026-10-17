---
id: PW-425
title: Fine zoom meander trains are perfectly regular at full swing
type: task
status: done
parent: null
subsystem: zoom
effort: s
impact: med
found_by: pw412
blocked_by: []
relates: [PW-405, PW-412, PW-416, PW-094]
refs: [planet/zoom_fine.py, _courses, _river_phase, "zoom 352c76 (scratch regen, 3453b8 -> 25 m)"]
created: 2026-10-16
updated: 2026-10-16
---

## Description
With floors (PW-412), alluvial reaches now get their full meander swing (MEANDER_OMEGA 1.2 rad). The sine-generated trains are identical bend after bend: the same wavelength (11 widths) and the same swing all along a reach. In plan view they read as a drawn wave, not a river (e.g. 352c76, the 310 m^3/s river). Real trains vary: wavelengths scatter about ±30% around ~11 w, and bends are skewed and of uneven size.

Suggested fix (planet-fixed, so sibling zooms agree):
- In `_river_phase`, scale each node's phase increment by (1 + ~0.3 n), with n a planet-fixed fbm at the node.
- In `_courses`, scale the swing (om) by a smooth planet-fixed noise (about ±0.2 rad over a few wavelengths), still capped by the room.
- Optionally add a skew (Kinoshita third harmonic).

Keep the PW-405 test's 8-16 w mean wavelength.

PW-416 (migration over time) would make trains irregular anyway. This ticket is for the static fine zoom.

## Updates
- 2026-10-16: Status todo -> done. Done on branch worktree-agent-a0b8d885889258e9f (pw425). New planet/zoom_fine_meander.py: Kinoshita bends (swing, skew, flatness incl. compound loops) with planet-fixed per-bend noise in the channel phase phi, a local warp of the valley phase psi (mean wavelength kept per 3 wavelengths; tight loops take less valley), caps for floor room (all bends shrink together), bend radius and necks, eased over a quarter wavelength; big loops (swing > 1.6, 50% planet-fixed) cut off, their old arc an oxbow pool on the floor (stats.floodplain.oxbow_km2). 352c76: sinuosity_gentle 1.70/1.87 -> 1.48/1.83 (median/p90), wavelengths +-20%, 2 small oxbows; block rms 1.61 -> 1.62. Handoff docs/review/audit/pw425-handoff.md (incl. what PW-416 should evolve: per-sample phi, omega, js, jf, X from ZFM.train). Follow-up draft: oxbow crescents and scroll bars.
- 2026-10-16: Created from inbox draft draft-meander-trains-too-regular.md (found by pw412).
