---
title: "Default planets spend ~60% of their time in an icehouse (Earth ~10-30%): dT 0 is today's icehouse Earth and the thermostat steers back to it"
type: task
status: needs-decision
parent: PW-470
milestone: v2
subsystem: climate
effort: s
impact: high
found_by: ice-v2-stage0
blocked_by: []
relates: [PW-555]
refs: [docs/review/ice-v2/checkpoint-0.md, docs/review/ice-v2-criteria.md, planet/tectonics/earth.py]
---

## Description
Base assumption A0 (docs/review/ice-v2-criteria.md). Checkpoint 0 (10 L6 seeds x 1 Gyr, after a 300 Myr warm-up):
ice holding >= 20 m of sea level 26-100% of the time, median 62%; Earth's record ~10-30% (Phanerozoic ~30% counting
whole icehouses, less since 2.5 Ga). Every seed has an icehouse; few have a long ice-free era like the Mesozoic. Cause:
dT = 0 is today's (icehouse) Earth, the drift and the CO2 thermostat wander around the run's own mean, and the
Phanerozoic's mean climate is ~5-8 C warmer than today (Scotese et al. 2021).
Options:
- A: default `climate_offset` +3..+5 C (cheap; the Earth-like showcase keeps 0 or picks a moment). Check the icehouse
  share lands in ~15-40%.
- B: a thermostat baseline that targets a warmer long-run mean than today's climate (same effect, inside the carbon
  cycle; pairs with draft-co2-carbon-stock).
- C: keep icy defaults (a style choice: ice ages are a feature), and widen N3.
Lean: B together with the carbon stock, with A as a quick test on the 10 seeds first. Owner's call on whether
icy-by-default is wanted.
