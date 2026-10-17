---
id: PW-244
title: "V1: a reliable, finished, usable planet from a seed"
type: epic
status: todo
parent: null
subsystem: infra
effort: xl
impact: high
found_by: daniel
blocked_by: []
relates: [PW-013, PW-184, PW-100, PW-090, PW-358, PW-202, PW-037, PW-092, PW-213, PW-248, PW-099, PW-392, PW-405, PW-030]
refs: []
created: 2026-10-15
updated: 2026-10-16
---

## Description
Owner and coordinator agreed (2026-10-15). V1 = pick a seed and a few settings and, in reasonable time, reliably get a finished planet at a chosen moment: plausible and mutually consistent geology, climate, water, ice and life; browsable from globe to km-scale region; data usable outside the viewer. Gaps, in rough priority: (1) remake the showcase on current code and review it (PW-202); (2) health: a physics audit for weird or wrong shortcuts, and a multi-seed health sweep as a standing check; (3) climate fidelity, mainly rain (epic PW-013); (4) the run's ice in cold eras (PW-240); (5) life layer complete: soils, coastal life, vegetation in the time zoom (epic PW-184); (6) speed: an optimisation pass, not only a faster machine; (7) a one-command/one-button seed-to-finished-world flow; (8) export (PW-100); (9) a calibration re-tune once the physics settles. Deliberately not V1: resources PW-155, weather PW-156, hazards PW-098, species/civilisation PW-103, moons PW-216, game attributes PW-206.

## Updates
- 2026-10-16: Owner decision 2026-10-16 late night: PW-030 (real ice-age cycles) is in v1; it follows PW-366 in the run lane, before freezing run physics.
- 2026-10-16: Reliability target agreed with owner: the full health sweep (8 L6 + 3 L7 seeds, 1 Gyr) stays inside every envelope, with a little wiggle room for known outliers. A deep ice age is fine if the planet recovers (judge excursions by recovery, not by single frames). Speed: ~30-40 min per L7 planet is fine.
- 2026-10-16: Rescoped with owner after docs/review/v1-reassessment-2026-10-16.md. V1 blockers in order: PW-358 (+PW-300 re-check) then freeze run physics; PW-202 remake/review; glacial carving PW-037 then PW-092 (added: great lakes, glacial escarpments, smoothed landscapes); vegetation in the time zoom PW-213 (added); PW-248 one-command make + New planet button; PW-100 export with PW-099; fine zooms PW-392/PW-405. Rain (PW-015/016) demoted from a gap to the final calibration pass: rain exists and works, it is off mainly against Earth. Done gaps: PW-240/245/246. Speed target: owner considers ~30-40 min for an L7 planet fine; no optimisation work unless it nears 1 h. Reliability target: pending owner's view on the health sweep.
- 2026-10-15: Created.
