---
id: PW-364
title: L5 envelope world (seed 1, 340-400 Myr) falls into a -516 m icehouse under a small, unrelated change; arid share 7.7%
type: task
status: todo
parent: null
subsystem: climate
effort: s
impact: low
found_by: tectonics-night
blocked_by: []
relates: [PW-240, PW-338]
refs: [tests/test_envelopes.py, docs/review/audit/tectonics-night/pw338.patch, docs/review/audit/tectonics-night/state.py, docs/review/audit/tectonics-night/drycheck.py]
created: 2026-10-16
updated: 2026-10-16
---

## Description
`tests/test_envelopes.py::test_climate[1]` (L5, seed 1, arid share averaged over 340-400 Myr, band 12-45%)
fails with 7.7% when PW-338's patch is applied (a hotspot vent's recorded floor follows its ground; it only
changes how much crust vents take, so the run diverges chaotically). On that trajectory the planet passes
through a deep cold era: at 340 Myr global 12.4 C, land ice 10.3% of the surface, sea level -516 m; at 400 Myr
16 C, land 25.8% (flooded), arid 4%. Without the patch the same seed has ice 0.4-2.2%, sea -5..-44 m, arid
17-18% over 340-400 Myr. Arid share every 20 Myr from 100 Myr, with / without the patch: 26 29 33 30 30 33
38 36 36 29 25 16 10 10 7 4 / 27 25 31 29 30 30 35 35 34 32 25 20 17 18 18 18.

The 8-seed L6 health sweep with the patch is in range (arid medians 26-35%, no icehouse outlier), so this is one
trajectory's cold era (PW-240: icehouse sea below -250 m) meeting a single-seed, single-window test. Two things
to decide: whether an icehouse that deep and long (~60 Myr) is the PW-240 problem showing again (likely), and
whether the envelope test should keep sampling one seed's 340-400 Myr window (fragile to any change that
reshuffles the history). Then PW-338 can land.
- [ ] PW-338's patch merged with the envelope tests green, without loosening the band

## Updates
- 2026-10-16: Created from inbox draft draft-envelope-l5-icehouse-dry.md (found by tectonics-night).
