---
id: PW-563
title: One rain-vs-temperature rule for the run (exp(0.03 dT)) and the time zoom (exp(0.07 dT)); measure the cold-era moisture brake
type: task
status: todo
parent: PW-470
milestone: v2
subsystem: climate
effort: s
impact: med
found_by: ice-v2-stage0
blocked_by: []
relates: [PW-555, PW-308]
refs: [planet/climate.py, planet/icemass.py, tools/ice_probe.py]
created: 2026-10-22
updated: 2026-10-22
---

## Description
Base assumption A8 (docs/review/ice-v2-criteria.md). The run's climate rescales global rain to mean_mm x
exp(0.03 dT) (the hydrological sensitivity, ~2-3%/K: Held & Soden 2006), while the time zoom scales its rain
between full climates by exp(PRECIP_K dT) with PRECIP_K = 0.07 (Clausius-Clapeyron's vapour rate). The two ice
models then see different snow for the same cooling (the zoom ~4%/C more), which matters for option 2 (the run
running the zoom's ice core). Also: the global renormalisation sends the remaining rain to whatever sea is open, so
the self-starving brake of a deep era (Chandler & Sohl 2000) is weaker than in a GCM. Measure first with
`tools/ice_probe.py --stair` (snow on ice, snow gain vs dT; checkpoint 0 has Earth's), then pick one rule.

## Updates
- 2026-10-22: Created from inbox draft draft-rain-vs-temperature-run-zoom.md (found by ice-v2-stage0).
