---
id: PW-269
title: "Delta plain radius 3-5x below its own Earth calibration: G-B and Mekong come out river-dominated"
type: task
status: in-progress
parent: PW-245
subsystem: coast
effort: s
impact: med
found_by: audit-coast-zoom
blocked_by: []
relates: [PW-061]
refs: [planet/coast.py, planet/zoom.py, tests/test_coast.py, docs/review/audit/coast-zoom.md]
created: 2026-10-15
updated: 2026-10-15
---

## Description
`coast.plain_radius_km` (coast.py:528-533) is `clip(10 (Q/100)^0.35 (0.8 + 0.6 sf), 15, 300)` km. Its docstring
(and zoom.py:661) calibrate it on Nile ~150 km at 2,800 m³/s, Mississippi ~250 km at 17,000, Ganges-Brahmaputra
~350 km. The formula gives 26-45, 48-85 and 64-112 km. It has been like this since 961b903.

The radius sets the zoom's delta plain (a cause of PW-061's "fans are small") and the tidal prism (∝ R²) in
`galloway`. With real Q, sediment, waves and tides, `coast.galloway` gives G-B river 0.81-0.61 (river-dominated)
and Mekong river 0.78-0.63, but tide 0.86 and 0.71 at the docstring's radii. The module names both as
tide-dominated examples. Mississippi, Nile and Sao Francisco keep their types.

Fix: refit the coefficient to the stated sizes (about `40 (Q/1000)^0.35 (0.8 + 0.6 sf)`, cap ~350 km) and
check zoom deltas 00975d/f81832/ce4b72 again. Re-derive `test_delta_types_differ`'s thresholds from the new
outputs; don't widen them.
- [ ] plain_radius_km within ~30% of the docstring's three Earth sizes
- [ ] G-B and Mekong tide-dominated or mixed-tide with real inputs; Mississippi still river, Sao Francisco wave

## Updates
- 2026-10-15: Status todo -> in-progress. Fix agent started (owner approved leans, 2026-10-15).
- 2026-10-15: Created from inbox draft draft-audit-coast-zoom-delta-radius.md (found by audit-coast-zoom).
