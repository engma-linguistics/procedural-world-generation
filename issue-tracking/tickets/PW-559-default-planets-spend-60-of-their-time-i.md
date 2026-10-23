---
id: PW-559
title: "Default planets spend ~60% of their time in an icehouse (Earth ~10-30%): dT 0 is today's icehouse Earth and the thermostat steers back to it"
type: task
status: todo
parent: PW-470
milestone: v2
subsystem: climate
effort: s
impact: high
found_by: ice-v2-stage0
blocked_by: []
relates: [PW-555]
refs: [docs/review/ice-v2/checkpoint-0.md, docs/review/ice-v2-criteria.md, planet/tectonics/earth.py]
created: 2026-10-22
updated: 2026-10-23
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

## Updates
- 2026-10-23: Status needs-decision -> todo. Coordinator (2026-10-24): owner defers geophysics; not an owner question. The physics lane decides it against the v1/v2 north star (seed robustness first) when it reaches it.
- 2026-10-23: Milestone v1 -> v2 (owner approved shrinking v1 to its real gates, 2026-10-24; docs/review/board/triage-2026-10-24.md).
- 2026-10-23: After PW-576 (CO2 stock, mature start): full sweep icehouse share median 43% (14-95%), ice bar passes on 5/11 runs (was 2/10 in band). Too-long/too-common icehouses on L6 seeds 11, 77, 505 and all three L7 seeds. See PW-611.
- 2026-10-22: Created from inbox draft draft-default-climate-icier-than-earth.md (found by ice-v2-stage0).
